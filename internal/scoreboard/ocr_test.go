package scoreboard

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func TestOCRParsingAndAddress(t *testing.T) {
	stored := newOCRRuntime(&OCRSettings{Address: "http://localhost:18099/json", Field: "Time"})
	if stored.Address != defaultScoreSight || stored.targets["main"].Following || stored.active {
		t.Fatal("stored source not normalized/manual", stored)
	}
	for text, want := range map[string]int{"00:00": 0, "4:27": 267, "51:47": 3107, "10080:00": 604800} {
		got, err := parseOCRClock(text)
		if err != nil || got != want {
			t.Fatalf("%q: %d, %v", text, got, err)
		}
	}
	for _, text := range []string{"", "00:60", "1:2", "-1:20", "1:20.0", "1:20:00", " 01:00", "01:00\n", "O1:00", "10080:01", "9999999:00"} {
		if _, err := parseOCRClock(text); err == nil {
			t.Fatal("accepted malformed reading", text)
		}
	}
	for _, address := range []string{"http://127.0.0.1:18099", "http://localhost:18099/json", "https://192.168.1.25:18099/", "http://[::1]:18099"} {
		if _, err := normalizeScoreSight(address); err != nil {
			t.Fatal(address, err)
		}
	}
	for _, address := range []string{"file:///etc/passwd", "http://example.com", "http://8.8.8.8", "http://169.254.169.254", "http://0.0.0.0:18099", "http://127.0.0.1/a", "http://user:secret@127.0.0.1", "http://127.0.0.1?secret=x", "http://127.0.0.1:99999", "http://127.0.0.1#fragment"} {
		if _, err := normalizeScoreSight(address); err == nil {
			t.Fatal("accepted unsafe address", address)
		}
	}
}

func injectOCR(a *App, text, state string, at time.Time) {
	a.acceptOCR(a.ocrTicketLocked(), []scoreSightResult{{Name: "Unused score", Text: "999", State: "Success"}, {Name: "Time", Text: text, State: state}}, nil, at)
}

func TestOCROwnershipHoldTakeoverAndUnrelatedState(t *testing.T) {
	a := appForTest(t)
	if err := a.ConnectOCR(defaultScoreSight); err != nil {
		t.Fatal(err)
	}
	before := a.State()
	now := time.Now()
	injectOCR(a, "02:34", "SameNoChange", now)
	if a.State().Main.Display != before.Main.Display || a.State().OCR.Field != "Time" {
		t.Fatal("check must not change match clock; select Time")
	}
	if err := a.FollowOCR(); err != nil {
		t.Fatal(err)
	}
	if a.State().Main.Display != "02:34" || a.State().Main.State != "ocr" || a.main.value(now.Add(time.Hour)) != 154*time.Second {
		t.Fatal("internal clock advanced under OCR")
	}
	for _, text := range []string{"02:33", "02:33", "10:00", "00:00", "20:00"} {
		injectOCR(a, text, "Success", time.Now())
		if a.State().Main.Display != text {
			t.Fatal("pause/reset/zero not reflected", text, a.State().Main)
		}
	}
	for _, result := range []scoreSightResult{{Name: "Time", Text: "00:00", State: "FailedFilter"}, {Name: "Time", State: "Empty"}, {Name: "Time", Text: "garbage", State: "Success"}, {Name: "Other", Text: "00:00", State: "Success"}, {Name: "Time", Text: "00:00", State: "Unknown"}} {
		a.acceptOCR(a.ocrTicketLocked(), []scoreSightResult{result}, nil, time.Now())
		if a.State().Main.Display != "20:00" || a.State().OCR.CanFollow || a.State().OCR.Warning == "" {
			t.Fatal("bad/missing reading replaced held time", a.State())
		}
	}
	a.acceptOCR(a.ocrTicketLocked(), nil, errors.New("Disconnected."), time.Now())
	if a.State().Main.Display != "20:00" || a.State().OCR.Connection != "error" {
		t.Fatal("lost time on disconnect")
	}
	injectOCR(a, "04:59", "Success", time.Now())
	if a.State().Main.Display != "04:59" {
		t.Fatal("recovery did not resume existing follow ownership")
	}
	for _, which := range []string{"main", "both"} {
		for _, action := range []string{"start", "pause", "stop", "reset"} {
			if !errors.Is(a.ClockAction(which, action), errOCRFollowing) {
				t.Fatal("manual transport bypassed OCR ownership")
			}
		}
	}
	if !errors.Is(a.SetClock("main", 60, "down"), errOCRFollowing) || !errors.Is(a.AdjustClock("main", 1), errOCRFollowing) {
		t.Fatal("manual set/adjust bypassed ownership")
	}
	oldGeneration := a.ocrTicketLocked()
	a.TakeManualControl()
	if a.State().Main.State != "paused" || a.State().Main.Display != "04:59" {
		t.Fatal("takeover must retain paused value")
	}
	a.acceptOCR(oldGeneration, []scoreSightResult{{Name: "Time", Text: "00:00", State: "Success"}}, nil, time.Now())
	injectOCR(a, "00:01", "Success", time.Now())
	if a.State().Main.Display != "04:59" || a.State().OCR.Following {
		t.Fatal("late/manual-mode poll overwrote clock")
	}
	if err := a.ClockAction("main", "start"); err != nil {
		t.Fatal(err)
	}
	if a.State().Main.State != "running" {
		t.Fatal("manual restart failed")
	}
	if err := a.FollowOCR(); err != nil {
		t.Fatal(err)
	}
	if a.State().Main.Display != "00:01" {
		t.Fatal("explicit follow failed")
	}
	after := a.State()
	if after.HomeScore != before.HomeScore || after.AwayScore != before.AwayScore || after.HomeFouls != before.HomeFouls || after.AwayFouls != before.AwayFouls || after.Period != before.Period || after.HomeName != before.HomeName || after.AwayName != before.AwayName || after.Shot != before.Shot || after.Main.DurationSeconds != before.Main.DurationSeconds {
		t.Fatal("OCR changed unrelated/configured values")
	}
	if err := a.ClockAction("shot", "start"); err != nil {
		t.Fatal(err)
	}
	if a.State().Shot.State != "running" {
		t.Fatal("independent shot blocked")
	}
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	if a.State().Shot.State != "ready" {
		t.Fatal("do not infer source running from HTTP reads")
	}
}

func TestOCRAutoHideRestartAndFreshness(t *testing.T) {
	a := appForTest(t)
	_ = a.UpdateGame("shot_auto_hide", json.RawMessage("true"))
	_ = a.ConnectOCR(defaultScoreSight)
	injectOCR(a, "00:20", "Success", time.Now())
	_ = a.FollowOCR()
	if a.State().ShotVisible {
		t.Fatal("auto-hide did not use OCR match value")
	}
	injectOCR(a, "00:25", "SameNoChange", time.Now())
	if !a.State().ShotVisible {
		t.Fatal("OCR remaining value not used")
	}
	a.TakeManualControl()
	_ = a.SetClock("main", 60, "up")
	_ = a.FollowOCR()
	injectOCR(a, "00:40", "Success", time.Now())
	if a.State().ShotVisible {
		t.Fatal("count-up remaining duration not used")
	}
	_ = a.ClockAction("shot", "start")
	shotAnchor := a.shot.Anchor
	injectOCR(a, "00:41", "SameNoChange", time.Now())
	if a.shot.Anchor != shotAnchor || a.shot.State != "running" {
		t.Fatal("auto-hide changed shot state")
	}
	a.mu.Lock()
	a.ocr.targets["main"].changedAt = time.Now().Add(-5 * time.Second)
	a.mu.Unlock()
	injectOCR(a, "00:41", "SameNoChange", time.Now())
	view := a.State().OCR
	if view.Freshness != "unavailable" || !strings.Contains(view.Warning, "paused or stale") || view.ValueChangeAgeMS < 5000 {
		t.Fatal("cached responses falsely proved freshness", view)
	}
	c, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(c, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if restarted.State().OCR.Following || restarted.State().OCR.Connection != "disconnected" || restarted.State().Main.State != "ready" {
		t.Fatal("restart resumed OCR")
	}
}

func TestScoreSightWireValidation(t *testing.T) {
	for _, body := range []string{`{"Time":"00:00"}`, `null`, strings.Repeat("x", ocrBodyLimit+1)} {
		source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { fmt.Fprint(w, body) }))
		_, err := fetchScoreSight(context.Background(), source.Client(), source.URL)
		source.Close()
		if err == nil {
			t.Fatal("invalid wire response accepted")
		}
	}
}

func TestOCRLoopBoundedNoOverlapRecoveryAndTakeover(t *testing.T) {
	var active, maxActive, calls, mode atomic.Int32
	entered := make(chan struct{}, 1)
	source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/json" || r.Header.Get("Authorization") != "" {
			t.Error("unexpected outbound request")
		}
		n := active.Add(1)
		defer active.Add(-1)
		for previous := maxActive.Load(); n > previous && !maxActive.CompareAndSwap(previous, n); previous = maxActive.Load() {
		}
		calls.Add(1)
		switch mode.Load() {
		case 1:
			w.WriteHeader(503)
			return
		case 2:
			select {
			case entered <- struct{}{}:
			default:
			}
			select {
			case <-r.Context().Done():
				return
			case <-time.After(2 * time.Second):
			}
		}
		fmt.Fprint(w, `[{"name":"Time","text":"12:34","state":"SameNoChange"}]`)
	}))
	defer source.Close()
	a := appForTest(t)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	done := make(chan struct{})
	go func() { a.RunOCR(ctx); close(done) }()
	if err := a.ConnectOCR(source.URL); err != nil {
		t.Fatal(err)
	}
	waitFor := func(predicate func() bool) {
		t.Helper()
		deadline := time.Now().Add(3 * time.Second)
		for time.Now().Before(deadline) {
			if predicate() {
				return
			}
			time.Sleep(10 * time.Millisecond)
		}
		t.Fatal("OCR condition timed out", a.State().OCR)
	}
	waitFor(func() bool { return a.State().OCR.CanFollow })
	_ = a.FollowOCR()
	mode.Store(1)
	waitFor(func() bool { return a.State().OCR.Connection == "error" })
	if a.State().Main.Display != "12:34" {
		t.Fatal("HTTP failure lost clock")
	}
	mode.Store(0)
	waitFor(func() bool { return a.State().OCR.Connection == "connected" })
	mode.Store(2)
	select {
	case <-entered:
	case <-time.After(2 * time.Second):
		t.Fatal("no blocking request")
	}
	start := time.Now()
	a.TakeManualControl()
	if time.Since(start) > 100*time.Millisecond {
		t.Fatal("takeover waited on source network")
	}
	waitFor(func() bool { return a.State().OCR.Connection == "error" })
	mode.Store(0)
	waitFor(func() bool { return a.State().OCR.CanFollow })
	if a.State().OCR.Following || a.State().Main.State != "paused" {
		t.Fatal("recovery overrode takeover")
	}
	if maxActive.Load() != 1 || calls.Load() > 30 {
		t.Fatal("overlapping or unbounded requests", maxActive.Load(), calls.Load())
	}
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second):
		t.Fatal("OCR loop did not shut down")
	}
}

func TestOCRAuthenticationAndOverlayPrivacy(t *testing.T) {
	a := appForTest(t)
	s, _ := NewServer(a)
	for _, path := range []string{"connect", "disconnect", "field", "follow", "manual"} {
		r := httptest.NewRequest("POST", "/api/ocr/"+path, strings.NewReader(`{}`))
		r.RemoteAddr = "192.168.1.23:1234"
		r.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		s.Handler().ServeHTTP(w, r)
		if w.Code != 401 {
			t.Fatal("remote OCR endpoint without auth", path, w.Code)
		}
	}
	r := httptest.NewRequest("POST", "/api/ocr/connect", strings.NewReader(`{"address":"http://127.0.0.1:18099"}`))
	r.RemoteAddr = "192.168.1.23:1234"
	r.Header.Set("Content-Type", "application/json")
	r.Header.Set("Authorization", "Bearer "+a.Config().Token)
	w := httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 200 {
		t.Fatal("authenticated OCR connect failed", w.Code, w.Body.String())
	}
	for _, body := range []string{"{}", `{"extra":true}`} {
		r = httptest.NewRequest("POST", "/api/ocr/manual", strings.NewReader(body))
		r.RemoteAddr = "127.0.0.1:1234"
		w = httptest.NewRecorder()
		s.Handler().ServeHTTP(w, r)
		if w.Code != 400 {
			t.Fatal("non-JSON takeover accepted")
		}
	}
	a.SetActiveListen("0.0.0.0:8790")
	r = httptest.NewRequest("GET", "/api/overlay-state", nil)
	r.RemoteAddr = "192.168.1.23:1234"
	w = httptest.NewRecorder()
	s.Handler().ServeHTTP(w, r)
	if w.Code != 200 || strings.Contains(w.Body.String(), `"ocr"`) || strings.Contains(w.Body.String(), "18099") || strings.Contains(w.Body.String(), a.Config().Token) {
		t.Fatal("overlay leaked OCR metadata/token")
	}
}

func TestOCRRedirectNotFollowed(t *testing.T) {
	var targetCalls atomic.Int32
	target := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { targetCalls.Add(1); fmt.Fprint(w, `[]`) }))
	defer target.Close()
	source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, target.URL+"/json", http.StatusFound)
	}))
	defer source.Close()
	a := appForTest(t)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go a.RunOCR(ctx)
	if err := a.ConnectOCR(source.URL); err != nil {
		t.Fatal(err)
	}
	deadline := time.Now().Add(2 * time.Second)
	for a.State().OCR.Connection != "error" && time.Now().Before(deadline) {
		time.Sleep(10 * time.Millisecond)
	}
	if a.State().OCR.Connection != "error" || targetCalls.Load() != 0 {
		t.Fatal("redirect was followed or no error reported")
	}
}
