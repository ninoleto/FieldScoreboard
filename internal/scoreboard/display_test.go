package scoreboard

import (
	"encoding/json"
	"reflect"
	"testing"
)

func TestImmediateDisplayIsolationAndPersistence(t *testing.T) {
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	acceptAll(a, allOCR("05:00", "24", "9", "8"))
	for _, target := range []string{"main", "shot", "home_score", "away_score", "home_fouls", "away_fouls", "period"} {
		followTarget(t, a, target)
	}
	before := a.Config()
	main, shot := a.main, a.shot
	stale := cloneLayout(before.Layout)
	patch := func(field string, value any) {
		t.Helper()
		raw, _ := json.Marshal(value)
		if err := a.UpdateDisplay(field, raw); err != nil {
			t.Fatal(field, err)
		}
	}
	patch("foul_style_home", "number")
	patch("foul_style_away", "number")
	patch("foul_dots_max", 20)
	patch("main_clock_format", "HH:MM:SS")
	patch("shot_clock_format", "MM:SS")
	after := a.Config()
	expected := before
	expected.Layout = after.Layout
	if !reflect.DeepEqual(expected, after) || a.main != main || a.shot != shot {
		t.Fatal("display changed game, clocks or ownership")
	}
	for _, target := range a.State().OCR.Targets {
		if !target.Following {
			t.Fatal("display changed ownership")
		}
	}
	element := stale.Elements["main_clock"]
	element.X = 777
	stale.Elements["main_clock"] = element
	if err := a.UpdateEditorLayout(stale); err != nil {
		t.Fatal(err)
	}
	saved := a.Config().Layout
	if saved.Elements["main_clock"].X != 777 || saved.FoulStyleHome != "number" || saved.FoulStyleAway != "number" || saved.FoulDotsMax != 20 || saved.MainClockFormat != "HH:MM:SS" || saved.ShotClockFormat != "MM:SS" {
		t.Fatal("stale editor Save rolled back live preferences", saved)
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(restarted.Config().Layout, saved) {
		t.Fatal("restart lost preferences")
	}
	for _, target := range restarted.State().OCR.Targets {
		if target.Following {
			t.Fatal("restart ownership")
		}
	}
	if err := a.SaveProfile("display"); err != nil {
		t.Fatal(err)
	}
	patch("foul_style_home", "dots")
	patch("main_clock_format", "SS")
	if err := a.LoadProfile("display"); err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(a.Config().Layout, saved) || a.main != main || a.shot != shot {
		t.Fatal("preset compatibility or clock isolation")
	}
	if err := a.UpdateLayout(stale); err != nil {
		t.Fatal(err)
	}
	if a.Config().Layout.FoulStyleHome != before.Layout.FoulStyleHome {
		t.Fatal("legacy full-layout compatibility")
	}
}

func TestDisplayValidationIsAtomic(t *testing.T) {
	a := appForTest(t)
	before := a.Config()
	for _, tc := range []struct{ field, raw string }{
		{"foul_style_home", `"invalid"`}, {"foul_style_away", `null`}, {"main_clock_format", `"bad"`}, {"shot_clock_format", `"HH:MM:SS"`},
		{"foul_dots_max", `0`}, {"foul_dots_max", `21`}, {"foul_dots_max", `1.5`}, {"foul_dots_max", `"5"`}, {"foul_dots_max", `null`}, {"home_score", `"123"`},
	} {
		if a.UpdateDisplay(tc.field, json.RawMessage(tc.raw)) == nil || !reflect.DeepEqual(a.Config(), before) {
			t.Fatal("invalid mutation", tc)
		}
	}
	for _, n := range []int{1, 20} {
		raw, _ := json.Marshal(n)
		if err := a.UpdateDisplay("foul_dots_max", raw); err != nil {
			t.Fatal(err)
		}
	}
}

func TestDisplayAPIAuthenticationAndStaleSave(t *testing.T) {
	a := appForTest(t)
	srv, err := NewServer(a)
	if err != nil {
		t.Fatal(err)
	}
	h := srv.Handler()
	stale, _ := json.Marshal(a.Config().Layout)
	body := `{"field":"foul_dots_max","value":9}`
	if w := apiCall(t, h, "/api/display", "POST", body, true, ""); w.Code != 401 {
		t.Fatal(w.Code)
	}
	if w := apiCall(t, h, "/api/display", "POST", body, true, a.Config().Token); w.Code != 200 {
		t.Fatal(w.Code, w.Body)
	}
	if w := apiCall(t, h, "/api/layout?preserve_display=1", "PUT", string(stale), true, ""); w.Code != 401 {
		t.Fatal(w.Code)
	}
	if w := apiCall(t, h, "/api/layout?preserve_display=1", "PUT", string(stale), false, ""); w.Code != 200 {
		t.Fatal(w.Code, w.Body)
	}
	if a.Config().Layout.FoulDotsMax != 9 {
		t.Fatal("stale save reverted preference")
	}
	before := a.Config()
	for _, body := range []string{`{"field":"foul_dots_max","value":21}`, `{"field":"foul_dots_max","value":3,"extra":1}`, `{}`} {
		if w := apiCall(t, h, "/api/display", "POST", body, false, ""); w.Code != 400 {
			t.Fatal(w.Code, w.Body)
		}
		if !reflect.DeepEqual(before, a.Config()) {
			t.Fatal("failed request changed config")
		}
	}
	if w := apiCall(t, h, "/api/layout?preserve_display=bad", "PUT", string(stale), false, ""); w.Code != 400 {
		t.Fatal(w.Code)
	}
}

func TestDisplayKeepsRunningClockAnchors(t *testing.T) {
	a := appForTest(t)
	if err := a.ClockAction("both", "start"); err != nil {
		t.Fatal(err)
	}
	main, shot := a.main, a.shot
	if err := a.UpdateDisplay("main_clock_format", json.RawMessage(`"SS"`)); err != nil {
		t.Fatal(err)
	}
	if err := a.UpdateDisplay("shot_clock_format", json.RawMessage(`"SS.t"`)); err != nil {
		t.Fatal(err)
	}
	if a.main != main || a.shot != shot {
		t.Fatal("display reset running clock anchors")
	}
}
