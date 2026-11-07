package scoreboard

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"
	"unicode"
)

const defaultScoreSight = "http://127.0.0.1:18099"
const ocrPollInterval = 200 * time.Millisecond
const ocrTimeout = 800 * time.Millisecond
const ocrBodyLimit = 256 * 1024

var errOCRFollowing = errors.New("take manual control of the OCR-controlled field first")
var ocrClockPattern = regexp.MustCompile(`^[0-9]{1,5}:[0-9]{2}$`)
var ocrNumberPattern = regexp.MustCompile(`^[0-9]{1,4}$`)
var ocrTargets = []string{"main", "shot", "home_score", "away_score", "home_fouls", "away_fouls", "period"}
var ocrSuggestions = map[string]string{"main": "Time", "shot": "Shot Clock", "home_score": "Home Score", "away_score": "Away Score", "home_fouls": "Home Fouls", "away_fouls": "Away Fouls", "period": "Period"}
var ocrLabels = map[string]string{"main": "Match clock", "shot": "Shot clock", "home_score": "Home score", "away_score": "Away score", "home_fouls": "Home fouls", "away_fouls": "Away fouls", "period": "Period"}

// Only settings persist. An explicit empty mapping disables auto-suggestion.
// Field retains compatibility with test.9 settings and mirrors the main mapping.
type OCRSettings struct {
	Address  string            `json:"address"`
	Field    string            `json:"field,omitempty"`
	Mappings map[string]string `json:"mappings,omitempty"`
}
type OCRTargetSnapshot struct {
	Field            string `json:"field"`
	Following        bool   `json:"following"`
	Reading          string `json:"reading"`
	Recognized       string `json:"recognized"`
	DetectionState   string `json:"detection_state"`
	LastAccepted     string `json:"last_accepted"`
	CanFollow        bool   `json:"can_follow"`
	ValueChangeAgeMS int64  `json:"value_change_age_ms"`
	Warning          string `json:"warning"`
}
type OCRSnapshot struct {
	// Legacy main aliases keep the test.9 read API compatible.
	OCRTargetSnapshot
	Address           string                       `json:"address"`
	Fields            []string                     `json:"fields"`
	Connection        string                       `json:"connection"`
	ResponseAgeMS     int64                        `json:"response_age_ms"`
	Freshness         string                       `json:"freshness"`
	ConnectionWarning string                       `json:"connection_warning"`
	Targets           map[string]OCRTargetSnapshot `json:"targets"`
}
type ocrTargetRuntime struct {
	OCRTargetSnapshot
	configured bool
	revision   uint64
	valid      bool
	value      int
	changedAt  time.Time
}
type ocrRuntime struct {
	Address    string
	Fields     []string
	Connection string
	warning    string
	targets    map[string]*ocrTargetRuntime
	active     bool
	generation uint64
	responseAt time.Time
}
type ocrTicket struct {
	generation uint64
	revisions  map[string]uint64
}

// ScoreSight 0.4.3 exposes no source/detection timestamp in /json.
type scoreSightResult struct {
	Name      string `json:"name"`
	Text      string `json:"text"`
	State     string `json:"state"`
	Malformed bool   `json:"-"`
}

func normalizeScoreSight(address string) (string, error) {
	u, err := url.Parse(strings.TrimSpace(address))
	if err != nil || u == nil || (u.Scheme != "http" && u.Scheme != "https") || u.User != nil || u.RawQuery != "" || u.Fragment != "" || u.RawPath != "" || (u.Path != "" && u.Path != "/" && u.Path != "/json") {
		return "", errors.New("use a ScoreSight HTTP(S) address without credentials, query or extra path")
	}
	host := u.Hostname()
	if host == "localhost" {
		host = "127.0.0.1" // ScoreSight's listener is IPv4; avoid DNS/proxy surprises.
	}
	ip := net.ParseIP(host)
	if ip == nil || !(ip.IsLoopback() || ip.IsPrivate() || isUsablePrivateIPv4(ip)) || ip.IsUnspecified() || ip.IsLinkLocalUnicast() {
		return "", errors.New("use localhost or a loopback/private LAN IP address for ScoreSight")
	}
	port := u.Port()
	if port != "" {
		n, err := strconv.Atoi(port)
		if err != nil || n < 1 || n > 65535 {
			return "", errors.New("invalid ScoreSight port")
		}
		u.Host = net.JoinHostPort(host, port)
	} else if strings.Contains(host, ":") {
		u.Host = "[" + host + "]"
	} else {
		u.Host = host
	}
	u.Path = ""
	return u.String(), nil
}

func validOCRField(field string) bool {
	return len(field) <= 128 && !strings.ContainsFunc(field, unicode.IsControl)
}

func parseOCRClock(text string) (int, error) {
	if !ocrClockPattern.MatchString(text) {
		return 0, errors.New("expected MM:SS")
	}
	parts := strings.Split(text, ":")
	minutes, _ := strconv.Atoi(parts[0])
	seconds, _ := strconv.Atoi(parts[1])
	if seconds > 59 || minutes*60+seconds > 7*86400 {
		return 0, errors.New("clock reading outside valid range")
	}
	return minutes*60 + seconds, nil
}

func parseOCRValue(target, text string) (int, error) {
	if target == "main" {
		return parseOCRClock(text)
	}
	if target == "shot" && strings.Contains(text, ":") {
		value, err := parseOCRClock(text)
		if err == nil && value <= 3600 {
			return value, nil
		}
		return 0, errors.New("expected seconds or MM:SS, at most 3600 seconds")
	}
	minimum, limit, digits := 0, 999, 3
	switch target {
	case "shot":
		limit, digits = 3600, 4
	case "home_fouls", "away_fouls":
		limit, digits = 30, 2
	case "period":
		minimum, limit, digits = 1, 20, 2
	case "home_score", "away_score":
	default:
		return 0, errors.New("unknown OCR target")
	}
	value, err := strconv.Atoi(text)
	if !ocrNumberPattern.MatchString(text) || err != nil || value < minimum || value > limit || len(text) > digits {
		return 0, fmt.Errorf("expected a whole number from %d to %d", minimum, limit)
	}
	return value, nil
}
func cloneOCRSettings(s *OCRSettings) *OCRSettings {
	if s == nil {
		return nil
	}
	c := *s
	c.Mappings = map[string]string{}
	for k, v := range s.Mappings {
		c.Mappings[k] = v
	}
	return &c
}
func newOCRRuntime(settings *OCRSettings) ocrRuntime {
	o := ocrRuntime{Address: defaultScoreSight, Fields: []string{}, Connection: "disconnected", targets: map[string]*ocrTargetRuntime{}}
	if settings != nil {
		o.Address = settings.Address
		if n, e := normalizeScoreSight(o.Address); e == nil {
			o.Address = n
		}
	}
	for _, target := range ocrTargets {
		t := &ocrTargetRuntime{OCRTargetSnapshot: OCRTargetSnapshot{Reading: "unconfigured"}}
		if settings != nil {
			t.Field, t.configured = settings.Mappings[target]
			if target == "main" && !t.configured && settings.Field != "" {
				t.Field, t.configured = settings.Field, true
			}
		}
		if t.Field != "" {
			t.Reading = "not_checked"
		}
		o.targets[target] = t
	}
	return o
}
func (a *App) ocrFollowingLocked(target string) bool {
	t := a.ocr.targets[target]
	return t != nil && t.Following
}
func (a *App) ocrGuardLocked(target string) error {
	if target == "both" {
		if a.ocrFollowingLocked("main") || a.ocrFollowingLocked("shot") {
			return fmt.Errorf("both clocks unchanged: %w before using combined clock controls", errOCRFollowing)
		}
	} else if a.ocrFollowingLocked(target) {
		return fmt.Errorf("%s: %w", ocrLabels[target], errOCRFollowing)
	}
	return nil
}
func (a *App) ocrSnapshotLocked(now time.Time) OCRSnapshot {
	v := OCRSnapshot{Address: a.ocr.Address, Fields: append([]string{}, a.ocr.Fields...), Connection: a.ocr.Connection, ResponseAgeMS: -1, Freshness: "unavailable", ConnectionWarning: a.ocr.warning, Targets: map[string]OCRTargetSnapshot{}}
	if !a.ocr.responseAt.IsZero() {
		v.ResponseAgeMS = now.Sub(a.ocr.responseAt).Milliseconds()
	}
	if v.Connection == "connected" && v.ResponseAgeMS >= 2000 {
		v.ConnectionWarning = "No recent response. Keeping the last accepted values."
	}
	for _, target := range ocrTargets {
		t := a.ocr.targets[target]
		view := t.OCRTargetSnapshot
		view.ValueChangeAgeMS = -1
		if !t.changedAt.IsZero() {
			view.ValueChangeAgeMS = now.Sub(t.changedAt).Milliseconds()
		}
		view.CanFollow = a.ocr.active && t.valid && v.Connection == "connected" && v.ResponseAgeMS >= 0 && v.ResponseAgeMS < 2000
		if t.valid && view.ValueChangeAgeMS >= 3000 {
			view.Warning = "Value unchanged: the source may be paused or stale."
		}
		v.Targets[target] = view
	}
	v.OCRTargetSnapshot = v.Targets["main"]
	return v
}
func (a *App) wakeOCRLocked() {
	select {
	case a.ocrWake <- struct{}{}:
	default:
	}
}
func (a *App) ocrSettingsLocked() *OCRSettings {
	s := &OCRSettings{Address: a.ocr.Address, Field: a.ocr.targets["main"].Field, Mappings: map[string]string{}}
	for k, t := range a.ocr.targets {
		if t.configured {
			s.Mappings[k] = t.Field
		}
	}
	return s
}
func (a *App) saveOCRSettingsLocked(s *OCRSettings) error {
	c := a.cfg
	c.OCR = s
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	return nil
}
func (a *App) ConnectOCR(address string) error {
	address, err := normalizeScoreSight(address)
	if err != nil {
		return err
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	for _, target := range ocrTargets {
		if err := a.ocrGuardLocked(target); err != nil {
			return err
		}
	}
	settings := &OCRSettings{Address: address}
	if address == a.ocr.Address {
		settings = a.ocrSettingsLocked()
	}
	if err := a.saveOCRSettingsLocked(settings); err != nil {
		return err
	}
	generation := a.ocr.generation + 1
	a.ocr = newOCRRuntime(settings)
	a.ocr.active, a.ocr.generation, a.ocr.Connection = true, generation, "connecting"
	a.wakeOCRLocked()
	return nil
}
func (a *App) SelectOCRField(field string) error { return a.SelectOCRMapping("main", field) }
func (a *App) SelectOCRMapping(target, field string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	t := a.ocr.targets[target]
	if t == nil {
		return errors.New("unknown OCR target")
	}
	if err := a.ocrGuardLocked(target); err != nil {
		return err
	}
	found := field == ""
	for _, name := range a.ocr.Fields {
		if name == field {
			found = true
		}
	}
	if !found {
		return errors.New("choose a field returned by ScoreSight")
	}
	settings := a.ocrSettingsLocked()
	settings.Mappings[target] = field
	if target == "main" {
		settings.Field = field
	}
	if err := a.saveOCRSettingsLocked(settings); err != nil {
		return err
	}
	revision := t.revision + 1
	*t = ocrTargetRuntime{configured: true, revision: revision, OCRTargetSnapshot: OCRTargetSnapshot{Field: field, Reading: "waiting"}}
	if field == "" {
		t.Reading = "unconfigured"
	}
	a.wakeOCRLocked()
	return nil
}
func (a *App) FollowOCR() error { return a.FollowOCRTarget("main") }
func (a *App) FollowOCRTarget(target string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	t := a.ocr.targets[target]
	if t == nil {
		return errors.New("unknown OCR target")
	}
	if !a.ocrSnapshotLocked(time.Now()).Targets[target].CanFollow {
		return errors.New("connect and wait for a valid reading before following this field")
	}
	if err := a.applyOCRValueLocked(target, t.value); err != nil {
		return err
	}
	t.Following = true
	t.revision++
	a.wakeOCRLocked()
	return nil
}
func (a *App) TakeManualControl() { _ = a.TakeOCRManual("main") }
func (a *App) TakeOCRManual(target string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	t := a.ocr.targets[target]
	if t == nil {
		return errors.New("unknown OCR target")
	}
	if t.Following {
		t.Following = false
		if target == "main" {
			a.main.State, a.main.Anchor = "paused", time.Time{}
		}
		if target == "shot" {
			a.shot.State, a.shot.Anchor = "paused", time.Time{}
		}
	}
	t.revision++
	return nil
}
func (a *App) applyOCRValueLocked(target string, value int) error {
	if target == "main" || target == "shot" {
		clock := &a.main
		if target == "shot" {
			clock = &a.shot
		}
		clock.Base = time.Duration(value) * time.Second
		clock.State, clock.Anchor = "paused", time.Time{}
		return nil
	}
	c := a.cfg
	var destination *int
	switch target {
	case "home_score":
		destination = &c.HomeScore
	case "away_score":
		destination = &c.AwayScore
	case "home_fouls":
		destination = &c.HomeFouls
	case "away_fouls":
		destination = &c.AwayFouls
	case "period":
		destination = &c.Period // Numeric observations never toggle OT.
	default:
		return errors.New("unknown OCR target")
	}
	if *destination == value {
		return nil
	}
	*destination = value
	// Persist changed game values only, never identical polling observations.
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	return nil
}

// Each request captures per-target revisions. Taking over one field invalidates
// its in-flight observation without dropping valid updates for other targets.
func (a *App) ocrTicketLocked() ocrTicket {
	ticket := ocrTicket{generation: a.ocr.generation, revisions: map[string]uint64{}}
	for k, t := range a.ocr.targets {
		ticket.revisions[k] = t.revision
	}
	return ticket
}
func (a *App) acceptOCR(ticket ocrTicket, results []scoreSightResult, fetchErr error, now time.Time) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if ticket.generation != a.ocr.generation || !a.ocr.active {
		return
	}
	if fetchErr != nil {
		a.ocr.Connection, a.ocr.warning = "error", fetchErr.Error()+" Keeping the last accepted values."
		for k, t := range a.ocr.targets {
			if ticket.revisions[k] == t.revision {
				t.valid = false
				t.Reading = "unavailable"
				t.Warning = "No reading available. Keeping the displayed value."
			}
		}
		return
	}
	a.ocr.Connection, a.ocr.responseAt, a.ocr.warning = "connected", now, ""
	byName := map[string]scoreSightResult{}
	for _, r := range results {
		if _, duplicate := byName[r.Name]; duplicate {
			r.Malformed = true
		}
		byName[r.Name] = r
	}
	a.ocr.Fields = []string{}
	for name := range byName {
		a.ocr.Fields = append(a.ocr.Fields, name)
	}
	sort.Strings(a.ocr.Fields)
	for _, target := range ocrTargets {
		t := a.ocr.targets[target]
		if ticket.revisions[target] != t.revision {
			continue
		}
		t.valid = false
		if !t.configured {
			if _, exists := byName[ocrSuggestions[target]]; exists {
				settings := a.ocrSettingsLocked()
				settings.Mappings[target] = ocrSuggestions[target]
				if target == "main" {
					settings.Field = ocrSuggestions[target]
				}
				if err := a.saveOCRSettingsLocked(settings); err != nil {
					t.Reading = "save_error"
					t.Warning = "Could not save suggested mapping."
					continue
				}
				t.Field, t.configured = ocrSuggestions[target], true
			}
		}
		t.Recognized, t.DetectionState, t.Warning = "", "", ""
		if t.Field == "" {
			t.Reading = "unconfigured"
			continue
		}
		r, exists := byName[t.Field]
		if !exists {
			t.Reading = "missing"
			t.Warning = "Selected field is missing. Keeping the displayed value."
			continue
		}
		t.Recognized, t.DetectionState = r.Text, r.State
		if r.Malformed {
			t.Reading = "malformed"
			t.Warning = "Malformed or duplicate source field. Keeping the displayed value."
			continue
		}
		if r.State != "Success" && r.State != "SameNoChange" {
			t.Reading = "rejected"
			t.Warning = "Reading rejected or empty. Keeping the displayed value."
			continue
		}
		value, err := parseOCRValue(target, r.Text)
		if err != nil {
			t.Reading = "malformed"
			t.Warning = err.Error() + ". Keeping the displayed value."
			continue
		}
		if t.Following {
			if err := a.applyOCRValueLocked(target, value); err != nil {
				t.Reading = "save_error"
				t.Warning = "Could not save value. Keeping the displayed value."
				continue
			}
		}
		if t.LastAccepted == "" || value != t.value {
			t.changedAt = now
		}
		t.value, t.valid, t.LastAccepted, t.Reading = value, true, r.Text, "accepted"
	}
}
func fetchScoreSight(ctx context.Context, client *http.Client, address string) ([]scoreSightResult, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, address+"/json", nil)
	if err != nil {
		return nil, errors.New("Invalid ScoreSight address.")
	}
	req.Header.Set("Accept", "application/json")
	req.Header.Set("Cache-Control", "no-cache, no-store")
	response, err := client.Do(req)
	if err != nil {
		return nil, errors.New("ScoreSight connection failed or timed out.")
	}
	defer response.Body.Close()
	if response.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ScoreSight returned HTTP %d.", response.StatusCode)
	}
	data, err := io.ReadAll(io.LimitReader(response.Body, ocrBodyLimit+1))
	if err != nil || len(data) > ocrBodyLimit {
		return nil, errors.New("ScoreSight response is incomplete or too large.")
	}
	var entries []json.RawMessage
	if err := json.Unmarshal(data, &entries); err != nil || entries == nil || len(entries) > 256 {
		return nil, errors.New("ScoreSight returned an invalid results array.")
	}
	// A corrupt or duplicate field must not prevent other fields from updating.
	results := []scoreSightResult{}
	indices := map[string]int{}
	for _, entry := range entries {
		var name struct {
			Name string `json:"name"`
		}
		if json.Unmarshal(entry, &name) != nil || name.Name == "" || !validOCRField(name.Name) {
			continue
		}
		var result scoreSightResult
		err := json.Unmarshal(entry, &result)
		result.Name = name.Name
		result.Malformed = err != nil || len(result.Text) > 256 || len(result.State) > 64
		if result.Malformed {
			result.Text, result.State = "", ""
		}
		if i, exists := indices[result.Name]; exists {
			results[i].Malformed = true
			continue
		}
		indices[result.Name] = len(results)
		results = append(results, result)
	}
	return results, nil
}

// One loop owns outbound requests: no overlapping polls, queues or HTTP handlers
// waiting on the source. Generation checks reject late results after takeover.
func (a *App) RunOCR(ctx context.Context) {
	a.ocrLoopOnce.Do(func() {
		transport := &http.Transport{Proxy: nil, DialContext: (&net.Dialer{Timeout: ocrTimeout}).DialContext, ResponseHeaderTimeout: ocrTimeout, MaxIdleConnsPerHost: 1}
		defer transport.CloseIdleConnections()
		client := &http.Client{Transport: transport, Timeout: ocrTimeout, CheckRedirect: func(*http.Request, []*http.Request) error { return errors.New("redirects are disabled") }}
		ticker := time.NewTicker(ocrPollInterval)
		defer ticker.Stop()
		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
			case <-a.ocrWake:
			}
			a.mu.Lock()
			active, address, ticket := a.ocr.active, a.ocr.Address, a.ocrTicketLocked()
			a.mu.Unlock()
			if !active {
				continue
			}
			results, err := fetchScoreSight(ctx, client, address)
			a.acceptOCR(ticket, results, err, time.Now())
		}
	})
}
