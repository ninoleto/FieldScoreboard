package scoreboard

import (
	"encoding/json"
	"errors"
	"net/http/httptest"
	"os"
	"reflect"
	"strings"
	"testing"
	"time"
)

func setOCRFormat(t *testing.T, a *App, enabled bool, format string) {
	t.Helper()
	if err := a.SetOCRTimeFormat(OCRTimeFormatSettings{Enabled: enabled, FinalMinuteFormat: format}); err != nil {
		t.Fatal(err)
	}
}

func TestOCRTimeFormatStrictParsing(t *testing.T) {
	for text, want := range map[string]time.Duration{
		"0": 0, "00": 0, "0.0": 0, "0.1": 100 * time.Millisecond,
		"9.7": 9700 * time.Millisecond, "55.4": 55400 * time.Millisecond,
		"59": 59 * time.Second, "59.9": 59900 * time.Millisecond,
		"00:59": 59 * time.Second, "1:00": time.Minute,
		"20:00": 20 * time.Minute, "10080:00": 7 * 24 * time.Hour,
	} {
		got, err := parseOCRObservation("main", text)
		if err != nil || got.clock != want {
			t.Fatalf("%q: got %v, %v; want %v", text, got, err, want)
		}
	}
	for _, text := range []string{"", "60", "60.0", "59.99", "055.4", ".4", "55.", "55,4", "55:4", "00:55.4", "00:60", "10080:01", "-1.0", "+1.0", " 55.4", "55.4\n", "5e1", "NaN", "５５.４", "time 55.4"} {
		if _, err := parseOCRObservation("main", text); err == nil {
			t.Fatal("accepted invalid time", text)
		}
	}
	for _, target := range ocrTargets {
		if target == "main" {
			continue
		}
		if _, err := parseOCRObservation(target, "1.2"); err == nil {
			t.Fatal("changed non-match validation", target)
		}
	}
}

func TestOCRTimeFormatTransitionsAndHold(t *testing.T) {
	for _, direction := range []string{"down", "up"} {
		t.Run(direction, func(t *testing.T) {
			a := appForTest(t)
			if err := a.SetClock("main", 1200, direction); err != nil {
				t.Fatal(err)
			}
			if err := a.UpdateDisplay("main_clock_format", json.RawMessage(`"HH:MM:SS"`)); err != nil {
				t.Fatal(err)
			}
			before := a.Config()
			setOCRFormat(t, a, true, "SS")
			if err := a.ConnectOCR(defaultScoreSight); err != nil {
				t.Fatal(err)
			}
			acceptAll(a, allOCR("01:01", "24", "7", "8"))
			followTarget(t, a, "main")
			followTarget(t, a, "home_score")
			for _, final := range []string{"SS", "SS.t"} {
				setOCRFormat(t, a, true, final)
				for _, step := range []struct {
					source, whole, tenth string
					ms                   int64
				}{
					{"01:01", "01:01", "01:01", 61000}, {"01:00", "01:00", "01:00", 60000},
					{"59.9", "59", "59.9", 59900}, {"55.4", "55", "55.4", 55400},
					{"55.3", "55", "55.3", 55300}, {"9.7", "09", "09.7", 9700},
					{"0.1", "00", "00.1", 100}, {"0.0", "00", "00.0", 0},
					{"20:00", "20:00", "20:00", 1200000}, {"00:59", "59", "59.0", 59000},
					{"1:00", "01:00", "01:00", 60000},
				} {
					injectOCR(a, step.source, "SameNoChange", time.Now())
					want := step.whole
					if final == "SS.t" {
						want = step.tenth
					}
					s := a.State()
					if s.Main.Display != want || s.Main.RemainingSeconds != float64(step.ms)/1000 || s.Main.State != "ocr" || s.OCR.LastAccepted != step.source {
						t.Fatal(step, s.Main, s.OCR)
					}
					if a.main.value(time.Now().Add(time.Hour)) != time.Duration(step.ms)*time.Millisecond {
						t.Fatal("independent OCR ticks")
					}
					srv, _ := NewServer(a)
					if srv.overlayState().Main != s.Main {
						t.Fatal("OBS differs from control snapshot")
					}
				}
			}
			injectOCR(a, "55.4", "Success", time.Now())
			for _, bad := range []scoreSightResult{
				{Name: "Time", Text: "0.0", State: "FailedFilter"}, {Name: "Time", State: "Empty"},
				{Name: "Time", Text: "0.0", State: "Unknown"}, {Name: "Time", Text: "00:60", State: "Success"},
				{Name: "Time", Text: "0.0", State: "Success", Malformed: true}, {Name: "Missing", Text: "0.0", State: "Success"},
			} {
				results := allOCR("00:00", "24", "9", "8")
				results[0] = bad
				acceptAll(a, results)
				if s := a.State(); s.Main.Display != "55.4" || s.Main.RemainingSeconds != 55.4 || s.HomeScore != 9 || s.OCR.CanFollow || s.OCR.Warning == "" {
					t.Fatal("invalid reading did not hold/isolate", s.Main, s.OCR)
				}
			}
			a.acceptOCR(a.ocrTicketLocked(), nil, errors.New("simulated loss"), time.Now())
			if s := a.State(); s.Main.Display != "55.4" || !s.OCR.Following || s.OCR.Connection != "error" {
				t.Fatal("loss changed held value", s.Main)
			}
			injectOCR(a, "54.9", "Success", time.Now())
			if a.State().Main.Display != "54.9" {
				t.Fatal("recovery")
			}
			ticket := a.ocrTicketLocked()
			a.TakeManualControl()
			wantManual := "00:00:55"
			if direction == "up" {
				wantManual = "00:00:54"
			}
			if s := a.State(); s.Main.Display != wantManual || s.Main.State != "paused" || s.Main.RemainingSeconds != 54.9 {
				t.Fatal("manual restore lost time/format", s.Main)
			}
			a.acceptOCR(ticket, allOCR("20:00", "14", "10", "8"), nil, time.Now())
			if s := a.State(); s.Main.RemainingSeconds != 54.9 || s.HomeScore != 10 {
				t.Fatal("takeover revision affected other fields", s.Main)
			}
			after := a.Config()
			if !reflect.DeepEqual(before.Layout, after.Layout) || before.MainDuration != after.MainDuration || before.MainDirection != after.MainDirection || a.State().Shot.RemainingSeconds != 24 {
				t.Fatal("unrelated configuration changed")
			}
			if err := a.ClockAction("main", "start"); err != nil || a.State().Main.State != "running" {
				t.Fatal("manual transport changed", err)
			}
		})
	}
}

func TestOCRTimeFormatPersistenceAndIsolation(t *testing.T) {
	a := appForTest(t)
	if a.State().OCR.MainTimeFormat != (OCRTimeFormatSettings{Enabled: false, FinalMinuteFormat: "SS", FinalMinuteStyle: "clean"}) {
		t.Fatal("legacy default")
	}
	_ = a.ConnectOCR(defaultScoreSight)
	acceptAll(a, allOCR("01:00", "24", "1", "2"))
	followTarget(t, a, "main")
	injectOCR(a, "55.4", "Success", time.Now())
	if a.State().Main.Display != "00:56" || a.State().OCR.Reading != "accepted" {
		t.Fatal("recognition depends on automatic display")
	}
	setOCRFormat(t, a, true, "SS.t")
	injectOCR(a, "55.4", "Success", time.Now())
	clock := a.main
	ticket := a.ocrTicketLocked()
	setOCRFormat(t, a, false, "SS.t")
	if a.main != clock || !a.State().OCR.Following || a.State().Main.Display != "00:56" {
		t.Fatal("disable changed held time or manual rounding")
	}
	a.acceptOCR(ticket, allOCR("55.3", "24", "1", "2"), nil, time.Now())
	if a.State().Main.RemainingSeconds != 55.3 {
		t.Fatal("presentation rejected an in-flight observation")
	}
	a.TakeManualControl()
	if err := a.FollowOCR(); err != nil {
		t.Fatal("explicit follow rejected a valid decimal", err)
	}
	injectOCR(a, "55.3", "Success", time.Now())
	if !a.State().OCR.CanFollow {
		t.Fatal("decimal rejected with automatic display off")
	}
	setOCRFormat(t, a, true, "SS.t")
	injectOCR(a, "55.3", "Success", time.Now())
	followTarget(t, a, "main")
	if err := a.SaveProfile("OCR format isolation"); err != nil {
		t.Fatal(err)
	}
	setOCRFormat(t, a, true, "SS")
	if err := a.LoadProfile("OCR format isolation"); err != nil {
		t.Fatal(err)
	}
	if a.State().OCR.MainTimeFormat.FinalMinuteFormat != "SS" {
		t.Fatal("profile overwrote OCR preference")
	}
	if err := a.UpdateEditorLayout(a.Config().Layout); err != nil {
		t.Fatal(err)
	}
	if !a.State().OCR.MainTimeFormat.Enabled {
		t.Fatal("layout save overwrote OCR preference")
	}
	setOCRFormat(t, a, true, "SS.t")
	copy := a.Config()
	copy.OCR.MainTimeFormat.Enabled = false
	if !a.State().OCR.MainTimeFormat.Enabled {
		t.Fatal("settings not deep copied")
	}
	a.DisconnectOCR()
	if s := a.State(); s.Main.Display != "00:56" || s.Main.RemainingSeconds != 55.3 || s.Main.State != "paused" {
		t.Fatal("disconnect lost manual display/precision", s.Main)
	}
	// Changing the source clears old mappings, but keeps this visual preference.
	if err := a.ConnectOCR("http://127.0.0.1:18098"); err != nil {
		t.Fatal(err)
	}
	if !a.State().OCR.MainTimeFormat.Enabled || a.State().OCR.Following {
		t.Fatal("reconnect settings/ownership")
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	s := restarted.State()
	if s.OCR.MainTimeFormat != (OCRTimeFormatSettings{Enabled: true, FinalMinuteFormat: "SS.t", FinalMinuteStyle: "clean"}) || s.OCR.Connection != "disconnected" || s.OCR.Following || s.Main.State != "ready" || s.Main.Display != "20:00" {
		t.Fatal("restart", s.Main, s.OCR)
	}
	for _, target := range s.OCR.Targets {
		if target.Following {
			t.Fatal("restart auto-follow")
		}
	}
	// Omitted optional fields in an existing OCR config retain defaults.
	cfg.OCR.MainTimeFormat = &OCRTimeFormatSettings{Enabled: true}
	legacy, err := NewApp(cfg, a.path)
	if err != nil || legacy.State().OCR.MainTimeFormat.FinalMinuteFormat != "SS" {
		t.Fatal("optional format default", err)
	}
	cfg.OCR.MainTimeFormat.FinalMinuteFormat = "MM:SS"
	if _, err := NewApp(cfg, a.path); err == nil {
		t.Fatal("invalid saved format accepted")
	}
	// A failed write must not change runtime policy or configuration.
	before := a.Config()
	a.path = t.TempDir()
	if err := a.SetOCRTimeFormat(OCRTimeFormatSettings{Enabled: false, FinalMinuteFormat: "SS", FinalMinuteStyle: "clean"}); err == nil {
		t.Fatal("expected save failure")
	}
	if !reflect.DeepEqual(before, a.Config()) {
		t.Fatal("failed save changed settings")
	}
}

func TestOCRTimeFormatAPI(t *testing.T) {
	a := appForTest(t)
	srv, _ := NewServer(a)
	valid := `{"enabled":true,"final_minute_format":"SS.t"}`
	call := func(body, contentType, remote, token string) *httptest.ResponseRecorder {
		r := httptest.NewRequest("POST", "/api/ocr/time-format", strings.NewReader(body))
		r.RemoteAddr = remote
		r.Header.Set("Content-Type", contentType)
		if token != "" {
			r.Header.Set("Authorization", "Bearer "+token)
		}
		w := httptest.NewRecorder()
		srv.Handler().ServeHTTP(w, r)
		return w
	}
	if w := call(valid, "application/json", "192.168.1.23:1234", ""); w.Code != 401 {
		t.Fatal("unauthenticated settings", w.Code)
	}
	for _, body := range []string{`{}`, `{"enabled":null,"final_minute_format":"SS"}`, `{"enabled":"true","final_minute_format":"SS"}`, `{"enabled":true}`, `{"enabled":true,"final_minute_format":"MM:SS"}`, valid + `{}`, `{"enabled":true,"final_minute_format":"SS","target":"shot"}`} {
		if w := call(body, "application/json", "127.0.0.1:1234", ""); w.Code != 400 {
			t.Fatal("invalid body", body, w.Code)
		}
	}
	if w := call(valid, "text/plain", "127.0.0.1:1234", ""); w.Code != 400 {
		t.Fatal("content type", w.Code)
	}
	if w := call(valid, "application/json", "192.168.1.23:1234", a.Config().Token); w.Code != 200 {
		t.Fatal(w.Code, w.Body.String())
	}
	bytes, err := os.ReadFile(a.path)
	if err != nil || !strings.Contains(string(bytes), `"main_time_format"`) {
		t.Fatal("not persisted", err)
	}
	public, _ := json.Marshal(srv.overlayState())
	for _, secret := range []string{"ocr", "main_time_format", "18099", a.Config().Token} {
		if strings.Contains(string(public), secret) {
			t.Fatal("overlay leaked settings", secret)
		}
	}
}
