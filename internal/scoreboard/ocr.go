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

var errOCRFollowing = errors.New("take manual control before changing the match clock")
var ocrClockPattern = regexp.MustCompile(`^[0-9]{1,5}:[0-9]{2}$`)

// Only settings persist. Connection, observations and ownership always start off.
type OCRSettings struct {
	Address string `json:"address"`
	Field   string `json:"field"`
}

type OCRSnapshot struct {
	Address          string   `json:"address"`
	Field            string   `json:"field"`
	Fields           []string `json:"fields"`
	Following        bool     `json:"following"`
	Connection       string   `json:"connection"`
	Reading          string   `json:"reading"`
	Recognized       string   `json:"recognized"`
	DetectionState   string   `json:"detection_state"`
	LastAccepted     string   `json:"last_accepted"`
	CanFollow        bool     `json:"can_follow"`
	ResponseAgeMS    int64    `json:"response_age_ms"`
	ValueChangeAgeMS int64    `json:"value_change_age_ms"`
	Freshness        string   `json:"freshness"`
	Warning          string   `json:"warning"`
}

type ocrRuntime struct {
	OCRSnapshot
	active     bool
	generation uint64
	valid      bool
	seconds    int
	responseAt time.Time
	changedAt  time.Time
}

// ScoreSight 0.4.3 /json is an array, including rejected/empty detections.
// Neither this response nor its HTTP Date proves source/detection freshness.
type scoreSightResult struct {
	Name  string `json:"name"`
	Text  string `json:"text"`
	State string `json:"state"`
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

func newOCRRuntime(settings *OCRSettings) ocrRuntime {
	view := OCRSnapshot{Address: defaultScoreSight, Fields: []string{}, Connection: "disconnected", Reading: "not_checked", Freshness: "unavailable"}
	if settings != nil {
		view.Address, view.Field = settings.Address, settings.Field
		if normalized, err := normalizeScoreSight(view.Address); err == nil {
			view.Address = normalized
		}
	}
	return ocrRuntime{OCRSnapshot: view}
}

func (a *App) ocrSnapshotLocked(now time.Time) OCRSnapshot {
	v := a.ocr.OCRSnapshot
	v.Fields = append([]string{}, v.Fields...)
	v.ResponseAgeMS, v.ValueChangeAgeMS = -1, -1
	if !a.ocr.responseAt.IsZero() {
		v.ResponseAgeMS = now.Sub(a.ocr.responseAt).Milliseconds()
	}
	if !a.ocr.changedAt.IsZero() {
		v.ValueChangeAgeMS = now.Sub(a.ocr.changedAt).Milliseconds()
	}
	v.CanFollow = a.ocr.active && a.ocr.valid && v.Connection == "connected" && v.ResponseAgeMS >= 0 && v.ResponseAgeMS < 2000
	if v.Connection == "connected" && v.ResponseAgeMS >= 2000 {
		v.Warning = "No recent response. Keeping the last match time."
	} else if a.ocr.valid {
		v.Warning = "ScoreSight provides no detection timestamp. Video freshness cannot be verified."
		if v.ValueChangeAgeMS >= 3000 {
			v.Warning = "Value unchanged: the source may be paused or stale. Check the ScoreSight video."
		}
	}
	return v
}

func (a *App) wakeOCRLocked() {
	select {
	case a.ocrWake <- struct{}{}:
	default:
	}
}

func (a *App) ConnectOCR(address string) error {
	address, err := normalizeScoreSight(address)
	if err != nil {
		return err
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.ocr.Following {
		return errOCRFollowing
	}
	settings := &OCRSettings{Address: address}
	if address == a.ocr.Address {
		settings.Field = a.ocr.Field
	}
	c := a.cfg
	c.OCR = settings
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	generation := a.ocr.generation + 1
	a.ocr = newOCRRuntime(settings)
	a.ocr.active, a.ocr.generation = true, generation
	a.ocr.Connection, a.ocr.Reading = "connecting", "waiting"
	a.wakeOCRLocked()
	return nil
}

func (a *App) SelectOCRField(field string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.ocr.Following {
		return errOCRFollowing
	}
	found := false
	for _, name := range a.ocr.Fields {
		if name == field {
			found = true
		}
	}
	if !found || field == "" {
		return errors.New("choose a field returned by ScoreSight")
	}
	c := a.cfg
	c.OCR = &OCRSettings{Address: a.ocr.Address, Field: field}
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	a.ocr.Field, a.ocr.valid = field, false
	a.ocr.Recognized, a.ocr.DetectionState, a.ocr.LastAccepted = "", "", ""
	a.ocr.Reading, a.ocr.Warning = "waiting", "Waiting for the selected field."
	a.ocr.changedAt = time.Time{}
	a.ocr.generation++
	a.wakeOCRLocked()
	return nil
}

func (a *App) FollowOCR() error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if !a.ocrSnapshotLocked(time.Now()).CanFollow {
		return errors.New("connect and wait for a valid MM:SS reading before following OCR")
	}
	a.ocr.Following = true
	a.ocr.generation++ // An older in-flight result cannot cross ownership changes.
	a.applyOCRClockLocked()
	a.wakeOCRLocked()
	return nil
}

func (a *App) TakeManualControl() {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.ocr.Following {
		a.ocr.Following = false
		a.main.State, a.main.Anchor = "paused", time.Time{}
	}
	a.ocr.generation++
}

func (a *App) applyOCRClockLocked() {
	// Do not Set/Start, change configured duration/direction, or extrapolate time.
	a.main.Base = time.Duration(a.ocr.seconds) * time.Second
	a.main.State, a.main.Anchor = "paused", time.Time{}
}

func (a *App) acceptOCR(generation uint64, results []scoreSightResult, fetchErr error, now time.Time) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if generation != a.ocr.generation || !a.ocr.active {
		return
	}
	a.ocr.valid = false
	if fetchErr != nil {
		a.ocr.Connection, a.ocr.Reading = "error", "unavailable"
		a.ocr.Warning = fetchErr.Error() + " Keeping the last match time."
		return
	}
	a.ocr.Connection, a.ocr.responseAt = "connected", now
	fields := []string{}
	for _, result := range results {
		fields = append(fields, result.Name)
	}
	sort.Strings(fields)
	a.ocr.Fields = fields
	if a.ocr.Field == "" && len(fields) > 0 {
		a.ocr.Field = fields[0]
		for _, field := range fields {
			if field == "Time" {
				a.ocr.Field = field
			}
		}
	}
	a.ocr.Recognized, a.ocr.DetectionState = "", ""
	a.ocr.Reading, a.ocr.Warning = "missing", "Selected field is missing. Keeping the last match time."
	for _, result := range results {
		if result.Name != a.ocr.Field {
			continue
		}
		a.ocr.Recognized, a.ocr.DetectionState = result.Text, result.State
		if result.State != "Success" && result.State != "SameNoChange" {
			a.ocr.Reading, a.ocr.Warning = "rejected", "ScoreSight rejected or emptied this reading. Keeping the last match time."
			return
		}
		seconds, err := parseOCRClock(result.Text)
		if err != nil {
			a.ocr.Reading, a.ocr.Warning = "malformed", "Reading is not a valid MM:SS time. Keeping the last match time."
			return
		}
		if a.ocr.LastAccepted == "" || seconds != a.ocr.seconds {
			a.ocr.changedAt = now
		}
		a.ocr.seconds, a.ocr.valid = seconds, true
		a.ocr.LastAccepted, a.ocr.Reading = result.Text, "accepted"
		if a.ocr.Following {
			a.applyOCRClockLocked()
		}
		return
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
	var results []scoreSightResult
	if err := json.Unmarshal(data, &results); err != nil || results == nil || len(results) > 256 {
		return nil, errors.New("ScoreSight returned an invalid results array.")
	}
	seen := map[string]bool{}
	for _, result := range results {
		if result.Name == "" || !validOCRField(result.Name) || len(result.Text) > 256 || len(result.State) > 64 || seen[result.Name] {
			return nil, errors.New("ScoreSight returned invalid or duplicate fields.")
		}
		seen[result.Name] = true
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
			active, address, generation := a.ocr.active, a.ocr.Address, a.ocr.generation
			a.mu.Unlock()
			if !active {
				continue
			}
			results, err := fetchScoreSight(ctx, client, address)
			a.acceptOCR(generation, results, err, time.Now())
		}
	})
}
