package scoreboard

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"strings"
	"testing"
	"time"
)

func allOCR(main, shot, home, away string) []scoreSightResult {
	return []scoreSightResult{{Name: "Time", Text: main, State: "Success"}, {Name: "Shot Clock", Text: shot, State: "SameNoChange"}, {Name: "Home Score", Text: home, State: "Success"}, {Name: "Away Score", Text: away, State: "Success"}}
}
func acceptAll(a *App, results []scoreSightResult) {
	a.acceptOCR(a.ocrTicketLocked(), results, nil, time.Now())
}
func followTarget(t *testing.T, a *App, target string) {
	t.Helper()
	if err := a.FollowOCRTarget(target); err != nil {
		t.Fatal(target, err)
	}
}

func TestOCRIndependentStrictValidation(t *testing.T) {
	for _, test := range []struct {
		target, text string
		want         int
	}{
		{"main", "00:00", 0}, {"main", "10080:00", 604800}, {"shot", "0", 0}, {"shot", "24", 24}, {"shot", "00:24", 24}, {"shot", "60:00", 3600}, {"shot", "3600", 3600}, {"home_score", "0", 0}, {"home_score", "999", 999}, {"away_score", "007", 7},
	} {
		if got, err := parseOCRValue(test.target, test.text); err != nil || got != test.want {
			t.Fatal(test, got, err)
		}
	}
	for _, target := range ocrTargets {
		bad := []string{"", "-1", "+1", " 1", "1 ", "1.0", "1\n", "O1", "١", "1:2", "00:60", "00:00:01", "10080:01"}
		if target == "main" {
			bad = append(bad, "24")
		} else if target == "shot" {
			bad = append(bad, "3601", "60:01")
		} else {
			bad = append(bad, "1000", "0000", "00:01")
		}
		for _, text := range bad {
			if _, err := parseOCRValue(target, text); err == nil {
				t.Fatal("accepted invalid", target, text)
			}
		}
	}
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	initial := a.State()
	acceptAll(a, allOCR("05:00", "24", "12", "7"))
	for _, target := range ocrTargets {
		followTarget(t, a, target)
	}
	if a.main.value(time.Now().Add(time.Hour)) != 300*time.Second || a.shot.value(time.Now().Add(time.Hour)) != 24*time.Second {
		t.Fatal("OCR clocks extrapolated")
	}
	acceptAll(a, allOCR("00:00", "0", "0", "0"))
	s := a.State()
	if s.Main.Display != "00:00" || s.Shot.RemainingSeconds != 0 || s.HomeScore != 0 || s.AwayScore != 0 {
		t.Fatal("valid zero not applied", s)
	}
	acceptAll(a, allOCR("20:00", "30", "25", "15"))
	for _, bad := range []scoreSightResult{{Name: "Time", Text: "00:00", State: "FailedFilter"}, {Name: "Time", State: "Empty"}, {Name: "Time", Text: "00:60", State: "Success"}, {Name: "Other", Text: "00:00", State: "Success"}} {
		results := allOCR("00:00", "14", "26", "16")
		results[0] = bad
		acceptAll(a, results)
		s = a.State()
		if s.Main.Display != "20:00" || s.Shot.RemainingSeconds != 14 || s.HomeScore != 26 || s.AwayScore != 16 || s.OCR.Targets["main"].CanFollow {
			t.Fatal("one field blocked others", s)
		}
	}
	results := allOCR("19:59", "3601", "1000", "17")
	acceptAll(a, results)
	s = a.State()
	if s.Main.Display != "19:59" || s.Shot.RemainingSeconds != 14 || s.HomeScore != 26 || s.AwayScore != 17 {
		t.Fatal("invalid fields clamped or blocked valid fields", s)
	}
	if s.HomeFouls != initial.HomeFouls || s.AwayFouls != initial.AwayFouls || s.Period != initial.Period || s.PeriodOvertime != initial.PeriodOvertime || !reflect.DeepEqual(s.Layout, initial.Layout) || s.Main.DurationSeconds != initial.Main.DurationSeconds || s.Shot.DurationSeconds != initial.Shot.DurationSeconds {
		t.Fatal("unrelated state changed")
	}
}

func TestOCRMixedOwnershipGuardsAndDelayedResponses(t *testing.T) {
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	acceptAll(a, allOCR("05:00", "24", "12", "7"))
	followTarget(t, a, "main")
	followTarget(t, a, "home_score")
	if err := a.ClockAction("shot", "start"); err != nil {
		t.Fatal(err)
	}
	_ = a.ClockAction("shot", "reset")
	if a.State().Shot.State != "ready" {
		t.Fatal("inferred running from OCR match")
	}
	if err := a.AdjustScore("away_score", 1); err != nil {
		t.Fatal(err)
	}
	if err := a.AdjustScore("home_fouls", 1); err != nil {
		t.Fatal(err)
	}
	if err := a.UpdateGame("period", json.RawMessage("2")); err != nil {
		t.Fatal(err)
	}
	followTarget(t, a, "shot")
	followTarget(t, a, "away_score")
	for _, target := range []string{"main", "shot", "both"} {
		for _, action := range []string{"start", "pause", "stop", "reset"} {
			before := a.State()
			err := a.ClockAction(target, action)
			after := a.State()
			if !errors.Is(err, errOCRFollowing) || before.Main != after.Main || before.Shot != after.Shot {
				t.Fatal("transport partially changed clocks", target, action, err)
			}
			if target == "both" && !strings.Contains(err.Error(), "both clocks unchanged") {
				t.Fatal("unclear combined error", err)
			}
		}
	}
	for _, target := range []string{"main", "shot"} {
		if !errors.Is(a.SetClock(target, 30, "down"), errOCRFollowing) || !errors.Is(a.AdjustClock(target, 1), errOCRFollowing) {
			t.Fatal("clock bypass", target)
		}
	}
	for _, target := range []string{"home_score", "away_score"} {
		if !errors.Is(a.AdjustScore(target, 1), errOCRFollowing) || !errors.Is(a.UpdateGame(target, json.RawMessage("99")), errOCRFollowing) {
			t.Fatal("score bypass", target)
		}
	}
	before := a.State()
	if !errors.Is(a.GameReset(), errOCRFollowing) {
		t.Fatal("game reset bypass")
	}
	after := a.State()
	if before.HomeScore != after.HomeScore || before.AwayScore != after.AwayScore || before.HomeFouls != after.HomeFouls || before.Period != after.Period {
		t.Fatal("partial game reset")
	}
	ticket := a.ocrTicketLocked()
	_ = a.TakeOCRManual("main")
	_ = a.TakeOCRManual("home_score")
	a.acceptOCR(ticket, allOCR("00:00", "13", "999", "8"), nil, time.Now())
	s := a.State()
	if s.Main.Display != "05:00" || s.HomeScore != 12 || s.Shot.RemainingSeconds != 13 || s.AwayScore != 8 || s.Main.State != "paused" {
		t.Fatal("late result crossed target ownership or blocked others", s)
	}
	// Takeover followed by an explicit re-follow also invalidates old requests.
	followTarget(t, a, "main")
	a.acceptOCR(ticket, allOCR("00:00", "12", "999", "9"), nil, time.Now())
	if a.State().Main.Display != "05:00" || a.State().AwayScore != 9 {
		t.Fatal("old observation applied after re-follow")
	}
	_ = a.TakeOCRManual("main")
	if err := a.ClockAction("main", "start"); err != nil {
		t.Fatal(err)
	}
	mainAnchor := a.main.Anchor
	if !errors.Is(a.ClockAction("both", "pause"), errOCRFollowing) || a.main.Anchor != mainAnchor || a.main.State != "running" {
		t.Fatal("shot ownership did not atomically reject both")
	}
	_ = a.TakeOCRManual("shot")
	if a.shot.State != "paused" || a.State().Shot.RemainingSeconds != 12 {
		t.Fatal("shot takeover not held")
	}
	if err := a.ClockAction("shot", "reset"); err != nil || a.shot.State != "running" {
		t.Fatal("manual shot reset resume regression", err)
	}
}

func TestOCRSuggestionsPersistenceLegacyAndIsolation(t *testing.T) {
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	acceptAll(a, []scoreSightResult{{Name: "Other", Text: "12:34", State: "Success"}})
	for _, v := range a.State().OCR.Targets {
		if v.Field != "" || v.Following {
			t.Fatal("arbitrary field suggested")
		}
	}
	acceptAll(a, []scoreSightResult{{Name: "Time", Text: "12:34", State: "Success"}, {Name: "Home Score", Text: "4", State: "Success"}})
	if a.State().OCR.Targets["shot"].Field != "" || a.State().OCR.Targets["away_score"].Field != "" {
		t.Fatal("missing suggested fields configured")
	}
	_ = a.SelectOCRMapping("main", "")
	acceptAll(a, allOCR("05:00", "24", "4", "2"))
	if a.State().OCR.Targets["main"].Field != "" {
		t.Fatal("explicit unconfigured mapping overwritten")
	}
	followTarget(t, a, "home_score")
	followTarget(t, a, "shot")
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	for key, v := range restarted.State().OCR.Targets {
		if v.Following || v.Field != a.State().OCR.Targets[key].Field {
			t.Fatal("restart ownership/mapping", key)
		}
	}
	if restarted.State().OCR.Connection != "disconnected" || restarted.State().HomeScore != 4 || restarted.State().Shot.State != "ready" {
		t.Fatal("restart state")
	}
	copy := a.Config()
	copy.OCR.Mappings["shot"] = "corrupted"
	if a.Config().OCR.Mappings["shot"] != "Shot Clock" {
		t.Fatal("config mapping alias escaped lock")
	}
	legacy := a.Config()
	legacy.OCR = &OCRSettings{Address: defaultScoreSight, Field: "Custom time"}
	old, err := NewApp(legacy, a.path)
	if err != nil || old.State().OCR.Targets["main"].Field != "Custom time" {
		t.Fatal("test.9 config migration", err)
	}
	if err := a.SelectOCRMapping("bad", "Time"); err == nil {
		t.Fatal("unknown target")
	}
	if err := a.FollowOCRTarget("bad"); err == nil {
		t.Fatal("unknown follow")
	}
	if err := a.TakeOCRManual("bad"); err == nil {
		t.Fatal("unknown takeover")
	}
}

func TestOCRWireFieldIsolationAndEffectiveAutoHide(t *testing.T) {
	for _, body := range []string{
		`[{"name":"Time","text":0,"state":"Success"},{"name":"Home Score","text":"42","state":"Success"}]`,
		`[{"name":"Time","text":"00:00","state":"Success"},{"name":"Time","text":"00:01","state":"Success"},{"name":"Home Score","text":"42","state":"Success"}]`,
		`[{"name":"Time","text":"00:00","state":false},{"name":"Home Score","text":"42","state":"Success"},null]`,
	} {
		source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) { fmt.Fprint(w, body) }))
		results, err := fetchScoreSight(context.Background(), source.Client(), source.URL)
		source.Close()
		if err != nil {
			t.Fatal("bad field rejected whole response", err)
		}
		a := appForTest(t)
		_ = a.ConnectOCR(defaultScoreSight)
		acceptAll(a, allOCR("05:00", "24", "12", "7"))
		followTarget(t, a, "main")
		followTarget(t, a, "home_score")
		acceptAll(a, results)
		if a.State().Main.Display != "05:00" || a.State().HomeScore != 42 || a.State().OCR.Targets["main"].Reading != "malformed" {
			t.Fatal("wire field isolation failed")
		}
	}
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	_ = a.UpdateGame("shot_auto_hide", json.RawMessage("true"))
	acceptAll(a, allOCR("00:20", "24", "1", "2"))
	followTarget(t, a, "main")
	followTarget(t, a, "shot")
	if a.State().ShotVisible {
		t.Fatal("effective clock comparison")
	}
	acceptAll(a, allOCR("00:20", "14", "1", "2"))
	if !a.State().ShotVisible {
		t.Fatal("effective shot value not used")
	}
	acceptAll(a, allOCR("00:00", "0", "1", "2"))
	if a.State().ShotVisible {
		t.Fatal("expired match")
	}
}
