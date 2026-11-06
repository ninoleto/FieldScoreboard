package scoreboard

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func appForTest(t *testing.T) *App {
	t.Helper()
	c, e := DefaultConfig()
	if e != nil {
		t.Fatal(e)
	}
	p := filepath.Join(t.TempDir(), "config.json")
	if e = saveConfig(p, c); e != nil {
		t.Fatal(e)
	}
	a, e := NewApp(c, p)
	if e != nil {
		t.Fatal(e)
	}
	return a
}
func TestDefaultAndPersistence(t *testing.T) {
	a := appForTest(t)
	s := a.State()
	if s.Main.Display != "20:00" || s.Shot.Display != "24" || s.Period != 1 {
		t.Fatalf("unexpected initial state: %+v", s)
	}
	if err := a.AdjustScore("home_score", 3); err != nil {
		t.Fatal(err)
	}
	if err := a.UpdateGame("home_name", json.RawMessage(`"Ocean Team"`)); err != nil {
		t.Fatal(err)
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	if cfg.HomeScore != 3 || cfg.HomeName != "Ocean Team" {
		t.Fatalf("not persisted: %+v", cfg)
	}
	if err := a.AdjustScore("home_score", -4); err == nil {
		t.Fatal("negative score must fail")
	}
	if got := a.State().HomeScore; got != 3 {
		t.Fatalf("negative update was not rolled back: %d", got)
	}
}
func TestIndependentClocksAndStopwatch(t *testing.T) {
	a := appForTest(t)
	if err := a.ClockAction("main", "start"); err != nil {
		t.Fatal(err)
	}
	time.Sleep(110 * time.Millisecond)
	if a.State().Shot.State != "ready" {
		t.Fatal("shot clock unexpectedly started")
	}
	if err := a.ClockAction("main", "pause"); err != nil {
		t.Fatal(err)
	}
	s := a.State()
	if s.Main.State != "paused" || s.Shot.State != "ready" {
		t.Fatalf("bad pause: %+v", s)
	}
	if err := a.SetClock("main", 100, "up"); err != nil {
		t.Fatal(err)
	}
	if a.State().Main.Direction != "up" || a.State().Main.Display != "00:00" {
		t.Fatal("countup should start at zero")
	}
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	if err := a.ClockAction("both", "pause"); err != nil {
		t.Fatal(err)
	}
	if a.State().Shot.State != "paused" || a.State().Main.State != "paused" {
		t.Fatal("both pause did not pause both")
	}
	if err := a.SetClock("shot", 14, "up"); err == nil {
		t.Fatal("shot must reject count-up")
	}
	if err := a.SetClock("shot", 14, "down"); err != nil {
		t.Fatal(err)
	}
	if a.State().Shot.Display != "14" {
		t.Fatal("shot reset preset failed")
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if restarted.State().Main.State != "ready" {
		t.Fatal("restarted app resumed clock unexpectedly")
	}
}

// A shot-clock reset is a new possession. It must resume immediately while
// the match clock is running, without modifying the match clock itself.
func TestShotClockResetFollowsRunningMatchClock(t *testing.T) {
	a := appForTest(t)
	if err := a.SetClock("shot", 14, "down"); err != nil {
		t.Fatal(err)
	}
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	if err := a.AdjustClock("shot", -9); err != nil {
		t.Fatal(err)
	}
	before := a.State()
	if before.Main.State != "running" || before.Shot.Display != "05" {
		t.Fatalf("precondition failed: %+v", before)
	}
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	after := a.State()
	if after.Main.State != "running" || after.Shot.State != "running" || after.Shot.Display != "14" {
		t.Fatalf("reset should immediately resume shot while match clock runs: %+v", after)
	}
	if after.Main.RemainingSeconds > before.Main.RemainingSeconds+0.02 {
		t.Fatalf("shot reset must not reset match clock: before=%v after=%v", before.Main.RemainingSeconds, after.Main.RemainingSeconds)
	}
	// Repeat after a shot-clock expiration while the main timer still runs.
	if err := a.AdjustClock("shot", -14); err != nil {
		t.Fatal(err)
	}
	if a.State().Shot.State != "completed" {
		t.Fatal("shot clock must have completed")
	}
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "running" || s.Shot.Display != "14" {
		t.Fatalf("reset after expiry must restart while match runs: %+v", s)
	}
}

func TestShotClockResetWhenMatchNotRunning(t *testing.T) {
	a := appForTest(t)
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "ready" {
		t.Fatalf("shot must stay ready when match is ready: %+v", s)
	}
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	if err := a.ClockAction("both", "pause"); err != nil {
		t.Fatal(err)
	}
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "ready" || s.Main.State != "paused" {
		t.Fatalf("shot must remain ready if main clock is paused: %+v", s)
	}
	if err := a.ClockAction("main", "start"); err != nil {
		t.Fatal(err)
	}
	if err := a.SetClock("shot", 24, "down"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "running" || s.Shot.Display != "24" {
		t.Fatalf("shot preset/set must continue when match is running: %+v", s)
	}
	if err := a.ClockAction("main", "pause"); err != nil {
		t.Fatal(err)
	}
	if err := a.SetClock("shot", 14, "down"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "ready" || s.Shot.Display != "14" {
		t.Fatalf("setting shot during pause must not auto-start: %+v", s)
	}
}

func TestShotOneSecondAdjustmentWhileRunningAndPaused(t *testing.T) {
	a := appForTest(t)
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	before := a.State()
	if err := a.AdjustClock("shot", -1); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.Display != "23" || s.Shot.State != "running" {
		t.Fatalf("-1s shot adjustment must not pause: %+v", s)
	}
	if err := a.AdjustClock("shot", 1); err != nil {
		t.Fatal(err)
	}
	after := a.State()
	if after.Shot.Display != "24" || after.Shot.State != "running" || after.Main.State != "running" {
		t.Fatalf("+1s shot adjustment must not pause: %+v", after)
	}
	if after.Main.RemainingSeconds > before.Main.RemainingSeconds+0.02 {
		t.Fatal("shot adjustments affected match clock")
	}
	if err := a.ClockAction("both", "pause"); err != nil {
		t.Fatal(err)
	}
	if err := a.AdjustClock("shot", -1); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Shot.State != "paused" || s.Shot.Display != "23" {
		t.Fatalf("shot adjustment should preserve paused state: %+v", s)
	}
	if err := a.AdjustClock("main", -1); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Main.State != "paused" {
		t.Fatal("main -1s must remain paused")
	}
	if err := a.AdjustClock("main", 1); err != nil {
		t.Fatal(err)
	}
}

func TestClockTickFormattingAndCompletion(t *testing.T) {
	c := newClock(24, "down")
	if got := clockDisplay(c.value(time.Now()), "SS", "down"); got != "24" {
		t.Fatal(got)
	}
	c.Anchor = time.Now().Add(-23*time.Second - 900*time.Millisecond)
	c.State = "running"
	if got := clockDisplay(c.value(time.Now()), "SS.t", "down"); got != "00.1" {
		t.Fatalf("tenths should show last tenth, got %q", got)
	}
	c.Anchor = time.Now().Add(-25 * time.Second)
	c.settle(time.Now())
	if c.State != "completed" || clockDisplay(c.value(time.Now()), "SS", "down") != "00" {
		t.Fatal("should complete at zero")
	}
}
func TestLayoutAndProfiles(t *testing.T) {
	a := appForTest(t)
	l := a.State().Layout
	l.Elements["home_score"] = Element{X: 300, Y: 200, Size: 78, Visible: true, Font: "mono", Color: "#ffcc11", Align: "center", Bold: true}
	if err := a.UpdateLayout(l); err != nil {
		t.Fatal(err)
	}
	if err := a.SaveProfile("My Futsal"); err != nil {
		t.Fatal(err)
	}
	l.Elements["home_score"] = Element{X: 500, Y: 200, Size: 78, Visible: true, Font: "mono", Color: "#ffcc11", Align: "center", Bold: true}
	if err := a.UpdateLayout(l); err != nil {
		t.Fatal(err)
	}
	if err := a.LoadProfile("My Futsal"); err != nil {
		t.Fatal(err)
	}
	if a.State().Layout.Elements["home_score"].X != 300 {
		t.Fatal("profile failed to restore x")
	}
	if err := a.SaveProfile("../../unsafe"); err == nil {
		t.Fatal("traversal allowed")
	}
	l.FoulDotsMax = 21
	if err := ValidateLayout(l); err == nil {
		t.Fatal("invalid fouls dots allowed")
	}
}
func apiCall(t *testing.T, h http.Handler, path, method, body string, remote bool, token string) *httptest.ResponseRecorder {
	t.Helper()
	var data io.Reader
	if body != "" {
		data = strings.NewReader(body)
	}
	r := httptest.NewRequest(method, path, data)
	if body != "" {
		r.Header.Set("Content-Type", "application/json")
	}
	if remote {
		r.RemoteAddr = "192.168.1.31:54321"
	} else {
		r.RemoteAddr = "127.0.0.1:54321"
	}
	if token != "" {
		r.Header.Set("Authorization", "Bearer "+token)
	}
	w := httptest.NewRecorder()
	h.ServeHTTP(w, r)
	return w
}
func TestAPIAndLocalOnly(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	if w := apiCall(t, h, "/api/state", "GET", "", true, ""); w.Code != 401 {
		t.Fatalf("remote without token got %d", w.Code)
	}
	if w := apiCall(t, h, "/overlay", "GET", "", true, ""); w.Code != 403 {
		t.Fatalf("remote overlay got %d", w.Code)
	}
	if w := apiCall(t, h, "/api/token", "GET", "", true, a.Config().Token); w.Code != 403 {
		t.Fatal("remote token read permitted")
	}
	if w := apiCall(t, h, "/api/state", "GET", "", true, a.Config().Token); w.Code != 200 {
		t.Fatalf("authenticated remote status got %d", w.Code)
	}
	if w := apiCall(t, h, "/api/adjust", "POST", `{"field":"home_score","delta":2}`, false, ""); w.Code != 200 {
		t.Fatalf("adjust %d: %s", w.Code, w.Body.String())
	}
	if w := apiCall(t, h, "/api/clock/shot/set", "POST", `{"seconds":14,"direction":"down"}`, false, ""); w.Code != 200 {
		t.Fatal(w.Body.String())
	}
	if w := apiCall(t, h, "/api/layout", "PUT", `{"elements":{}}`, false, ""); w.Code != 400 {
		t.Fatal("invalid layout accepted")
	}
	if w := apiCall(t, h, "/api/clock/main/start", "GET", "", false, ""); w.Code != 404 {
		t.Fatal("GET changed clock")
	}
	if w := apiCall(t, h, "/api/events", "GET", "", true, ""); w.Code != 403 {
		t.Fatal("remote unauthenticated SSE allowed")
	}
	if w := apiCall(t, h, "/overlay", "GET", "", false, ""); w.Code != 200 || !strings.Contains(w.Body.String(), "overlayStage") {
		t.Fatalf("local overlay: %d %s", w.Code, w.Body.String())
	}
}
func TestAPIShotClockResetContinuesAndFineAdjustment(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	for _, endpoint := range []string{"/api/clock/both/start", "/api/clock/shot/reset"} {
		if w := apiCall(t, h, endpoint, "POST", "", false, ""); w.Code != 200 {
			t.Fatalf("%s: %d %s", endpoint, w.Code, w.Body.String())
		}
	}
	if s := a.State(); s.Main.State != "running" || s.Shot.State != "running" || s.Shot.Display != "24" {
		t.Fatalf("shot reset via API should continue running: %+v", s)
	}
	for _, tc := range []struct {
		seconds int
		want    string
	}{{-1, "23"}, {1, "24"}} {
		body := fmt.Sprintf(`{"seconds":%d}`, tc.seconds)
		w := apiCall(t, h, "/api/clock/shot/adjust", "POST", body, false, "")
		if w.Code != 200 {
			t.Fatalf("adjust %d: %d %s", tc.seconds, w.Code, w.Body.String())
		}
		if s := a.State(); s.Shot.Display != tc.want || s.Shot.State != "running" || s.Main.State != "running" {
			t.Fatalf("adjust %d: %+v", tc.seconds, s)
		}
	}
	if w := apiCall(t, h, "/api/clock/shot/set", "POST", `{"seconds":14,"direction":"down"}`, false, ""); w.Code != 200 {
		t.Fatalf("shot preset: %d %s", w.Code, w.Body.String())
	}
	if s := a.State(); s.Shot.Display != "14" || s.Shot.State != "running" {
		t.Fatalf("preset must start while match runs: %+v", s)
	}
	if w := apiCall(t, h, "/api/clock/both/pause", "POST", "", false, ""); w.Code != 200 {
		t.Fatalf("pause: %s", w.Body.String())
	}
	if w := apiCall(t, h, "/api/clock/shot/reset", "POST", "", false, ""); w.Code != 200 {
		t.Fatalf("reset: %s", w.Body.String())
	}
	if s := a.State(); s.Shot.State != "ready" || s.Main.State != "paused" {
		t.Fatalf("pause/reset must not start shot: %+v", s)
	}
}

func TestImageUploadAndBackground(t *testing.T) {
	a := appForTest(t)
	srv, _ := NewServer(a)
	im := image.NewRGBA(image.Rect(0, 0, 64, 64))
	im.Set(0, 0, color.White)
	var buf bytes.Buffer
	if err := png.Encode(&buf, im); err != nil {
		t.Fatal(err)
	}
	r := httptest.NewRequest("POST", "/api/background", bytes.NewReader(buf.Bytes()))
	r.Header.Set("Content-Type", "image/png")
	r.RemoteAddr = "127.0.0.1:12345"
	w := httptest.NewRecorder()
	srv.Handler().ServeHTTP(w, r)
	if w.Code != 200 {
		t.Fatalf("upload error %d %s", w.Code, w.Body.String())
	}
	ref := a.State().Layout.Background
	if len(ref) != 68 || !strings.HasSuffix(ref, ".png") {
		t.Fatalf("bad image ref %q", ref)
	}
	if _, err := os.Stat(filepath.Join(a.ConfigDir(), "backgrounds", ref)); err != nil {
		t.Fatal(err)
	}
	if resp := apiCall(t, srv.Handler(), "/background/"+ref, "GET", "", false, ""); resp.Code != 200 {
		t.Fatalf("background HTTP %d", resp.Code)
	}
	if err := a.SetBackground("../../etc/passwd"); err == nil {
		t.Fatal("path traversal allowed")
	}
	if w := apiCall(t, srv.Handler(), "/api/background", "DELETE", "", false, ""); w.Code != 200 {
		t.Fatal("remove background failed")
	}
}

func TestPeriodOvertimePersistsAndRestores(t *testing.T) {
	a := appForTest(t)
	if err := a.UpdateGame("period", json.RawMessage(`2`)); err != nil {
		t.Fatal(err)
	}
	if err := a.UpdateGame("period_overtime", json.RawMessage(`true`)); err != nil {
		t.Fatal(err)
	}
	s := a.State()
	if !s.PeriodOvertime || s.Period != 2 || s.PeriodLabel != "OT" {
		t.Fatalf("overtime should override numeric label: %+v", s)
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	b, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if !b.State().PeriodOvertime || b.State().PeriodLabel != "OT" {
		t.Fatal("OT preference not persisted")
	}
	if err = b.UpdateGame("period_overtime", json.RawMessage(`false`)); err != nil {
		t.Fatal(err)
	}
	if s = b.State(); s.Period != 2 || s.PeriodLabel != "2" {
		t.Fatalf("period was not restored: %+v", s)
	}
	if err = b.GameReset(); err != nil {
		t.Fatal(err)
	}
	if s = b.State(); s.Period != 1 || s.PeriodOvertime {
		t.Fatalf("game reset must clear OT: %+v", s)
	}
	if err = b.UpdateGame("period_overtime", json.RawMessage(`"yes"`)); err == nil {
		t.Fatal("invalid OT value accepted")
	}
}

func TestShotAutoHideOnlyAffectsOverlay(t *testing.T) {
	a := appForTest(t)
	if !a.State().ShotVisible {
		t.Fatal("new installs must preserve visible shot clock")
	}
	if err := a.UpdateGame("shot_auto_hide", json.RawMessage(`true`)); err != nil {
		t.Fatal(err)
	}
	if err := a.SetClock("main", 20, "down"); err != nil {
		t.Fatal(err)
	}
	// Shot clock 24 > period remaining 20; no need to show shot clock.
	if s := a.State(); s.ShotVisible || !s.ShotAutoHide || s.Shot.RemainingSeconds != 24 {
		t.Fatalf("expected hidden shot value without resetting it: %+v", s)
	}
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	if err := a.ClockAction("shot", "reset"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.ShotVisible || s.Shot.State != "running" || s.Main.State != "running" {
		t.Fatalf("reset must hide but keep running clock: %+v", s)
	}
	if err := a.SetClock("shot", 14, "down"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); !s.ShotVisible || s.Shot.State != "running" {
		t.Fatalf("shot should show below match time: %+v", s)
	}
	if err := a.SetClock("main", 10, "up"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.ShotVisible {
		t.Fatalf("count-up mode must use period duration minus elapsed: %+v", s)
	}
	if err := a.UpdateGame("shot_auto_hide", json.RawMessage(`false`)); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); !s.ShotVisible {
		t.Fatalf("manual off must show shot regardless of clock values: %+v", s)
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	if cfg.ShotAutoHide {
		t.Fatal("shot auto hide off not persisted")
	}
}
func TestShotAutoHideBoundaryAtEqualTime(t *testing.T) {
	a := appForTest(t)
	if err := a.UpdateGame("shot_auto_hide", json.RawMessage(`true`)); err != nil {
		t.Fatal(err)
	}
	if err := a.SetClock("main", 24, "down"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.ShotVisible {
		t.Fatal("equal shot/main time should hide")
	}
	if err := a.SetClock("main", 25, "down"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); !s.ShotVisible {
		t.Fatal("shot < main should remain visible")
	}
}
func TestNetworkDiscoveryAndListenerRestart(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	if w := apiCall(t, h, "/api/network-interfaces", "GET", "", true, a.Config().Token); w.Code != 403 {
		t.Fatalf("remote enumeration %d", w.Code)
	}
	w := apiCall(t, h, "/api/network-interfaces", "GET", "", false, "")
	if w.Code != 200 {
		t.Fatalf("local enumeration %d: %s", w.Code, w.Body.String())
	}
	var result NetworkInterfaces
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil {
		t.Fatal(err)
	}
	for _, iface := range result.Interfaces {
		if !isUsablePrivateIPv4(net.ParseIP(iface.IP)) {
			t.Fatalf("unsafe network address %q", iface.IP)
		}
	}
	if s := a.State(); s.RestartRequired || s.ActiveListen != "127.0.0.1:8790" {
		t.Fatalf("bad active initial listen: %+v", s)
	}
	w = apiCall(t, h, "/api/network", "PUT", `{"listen":"0.0.0.0:8790"}`, false, "")
	if w.Code != 200 {
		t.Fatal(w.Body.String())
	}
	if s := a.State(); !s.RestartRequired || s.ActiveListen != "127.0.0.1:8790" || s.Listen != "0.0.0.0:8790" {
		t.Fatalf("network restart not reported: %+v", s)
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if s := restarted.State(); s.RestartRequired || s.ActiveListen != "0.0.0.0:8790" {
		t.Fatalf("restart didn't apply listen: %+v", s)
	}
}

func TestNetworkOBSReadOnlyOverlayAndListenerRestart(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	for _, path := range []string{"/overlay", "/overlay.js", "/overlay.css", "/api/overlay-state", "/api/overlay-events"} {
		if w := apiCall(t, h, path, "GET", "", true, ""); w.Code != 403 {
			t.Fatalf("%s accessible remotely while LAN off: %d", path, w.Code)
		}
	}
	if err := a.UpdateListen("0.0.0.0:8790"); err != nil {
		t.Fatal(err)
	}
	if w := apiCall(t, h, "/api/overlay-state", "GET", "", true, ""); w.Code != 403 {
		t.Fatal("saved but unapplied listen must not expose overlay")
	}
	// Restart applies the LAN bind; the new OBS read-only endpoints now work.
	a.SetActiveListen("0.0.0.0:8790")
	for _, path := range []string{"/overlay", "/overlay.js", "/overlay.css", "/api/overlay-state"} {
		if w := apiCall(t, h, path, "GET", "", true, ""); w.Code != 200 {
			t.Fatalf("remote OBS %s: %d %s", path, w.Code, w.Body.String())
		}
	}
	r := apiCall(t, h, "/api/overlay-state", "GET", "", true, "")
	var overlay map[string]json.RawMessage
	if err := json.Unmarshal(r.Body.Bytes(), &overlay); err != nil {
		t.Fatal(err)
	}
	for _, secret := range []string{"token", "listen", "active_listen", "restart_required"} {
		if _, ok := overlay[secret]; ok {
			t.Fatalf("overlay must not disclose %s", secret)
		}
	}
	if _, ok := overlay["home_score"]; !ok {
		t.Fatal("overlay missing scoreboard values")
	}
	if w := apiCall(t, h, "/api/state", "GET", "", true, ""); w.Code != 401 {
		t.Fatal("remote API status unexpectedly exposed")
	}
	if w := apiCall(t, h, "/api/clock/main/start", "POST", "", true, ""); w.Code != 401 {
		t.Fatal("remote control unexpectedly exposed")
	}
	if w := apiCall(t, h, "/api/events", "GET", "", true, ""); w.Code != 403 {
		t.Fatal("full state SSE must stay local-only")
	}
	remote := httptest.NewRequest("GET", "/overlay", nil)
	remote.RemoteAddr = "8.8.8.8:4321"
	public := httptest.NewRecorder()
	h.ServeHTTP(public, remote)
	if public.Code != 403 {
		t.Fatalf("public-IP overlay accepted: %d", public.Code)
	}
	// Confirm the public overlay SSE streams and responds to context cancellation.
	ctx, cancel := context.WithCancel(context.Background())
	ev := httptest.NewRequest("GET", "/api/overlay-events", nil).WithContext(ctx)
	ev.RemoteAddr = "192.168.1.31:12345"
	w := httptest.NewRecorder()
	done := make(chan struct{})
	go func() { h.ServeHTTP(w, ev); close(done) }()
	time.Sleep(120 * time.Millisecond)
	cancel()
	select {
	case <-done:
	case <-time.After(time.Second):
		t.Fatal("overlay SSE did not stop after cancellation")
	}
	if !strings.Contains(w.Body.String(), `"home_score"`) {
		t.Fatal("remote overlay SSE missing sanitized scores")
	}
	if strings.Contains(w.Body.String(), `"active_listen"`) {
		t.Fatal("remote overlay SSE leaked listener metadata")
	}
}

func TestLocalOnlyTokenRotation(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	old := a.Config().Token
	if w := apiCall(t, h, "/api/token/rotate", "POST", "", true, old); w.Code != 415 && w.Code != 403 {
		t.Fatalf("remote rotate allowed: %d", w.Code)
	}
	if w := apiCall(t, h, "/api/token/rotate", "POST", "", false, ""); w.Code != 415 {
		t.Fatalf("CSRF-unsafe rotate accepted: %d", w.Code)
	}
	remote := httptest.NewRequest("POST", "/api/token/rotate", nil)
	remote.RemoteAddr = "192.168.1.31:12345"
	remote.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	h.ServeHTTP(w, remote)
	if w.Code != 403 {
		t.Fatalf("remote rotation was allowed: %d", w.Code)
	}
	local := httptest.NewRequest("POST", "/api/token/rotate", nil)
	local.RemoteAddr = "127.0.0.1:12345"
	local.Header.Set("Content-Type", "application/json")
	w = httptest.NewRecorder()
	h.ServeHTTP(w, local)
	if w.Code != 200 {
		t.Fatalf("local rotation: %d %s", w.Code, w.Body.String())
	}
	var result map[string]string
	if err := json.Unmarshal(w.Body.Bytes(), &result); err != nil {
		t.Fatal(err)
	}
	fresh := result["token"]
	if fresh == old || len(fresh) != 64 {
		t.Fatal("rotation didn't create a distinct 256-bit token")
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	if cfg.Token != fresh {
		t.Fatal("rotated token not persisted")
	}
	if w := apiCall(t, h, "/api/state", "GET", "", true, old); w.Code != 401 {
		t.Fatal("old token was not revoked")
	}
	if w := apiCall(t, h, "/api/state", "GET", "", true, fresh); w.Code != 200 {
		t.Fatal("new token cannot authenticate")
	}
}
