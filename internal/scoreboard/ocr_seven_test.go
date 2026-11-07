package scoreboard

import (
	"encoding/json"
	"errors"
	"reflect"
	"testing"
	"time"
)

func TestOCRFoulsPeriodOwnershipOTAndPersistence(t *testing.T) {
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	for target, values := range map[string][]string{"home_fouls": {"0", "30"}, "away_fouls": {"0", "30"}, "period": {"1", "20"}} {
		for _, v := range values {
			if _, err := parseOCRValue(target, v); err != nil {
				t.Fatal(target, v, err)
			}
		}
		invalid := []string{"-1", "31", "1.0", "OT", "00:01", "999", ""}
		if target == "period" {
			invalid = append(invalid, "0", "21")
		} else {
			invalid = append(invalid, " 1", "1 ")
		}
		for _, v := range invalid {
			if _, err := parseOCRValue(target, v); err == nil {
				t.Fatal("invalid accepted", target, v)
			}
		}
	}
	results := allOCR("05:00", "24", "10", "9")
	results[4].Text = "3"
	results[5].Text = "2"
	results[6].Text = "4"
	acceptAll(a, results)
	_ = a.UpdateGame("period_overtime", json.RawMessage("true"))
	for _, target := range ocrTargets {
		followTarget(t, a, target)
	}
	s := a.State()
	if s.HomeFouls != 3 || s.AwayFouls != 2 || s.Period != 4 || s.PeriodLabel != "OT" {
		t.Fatal("seven targets / OT", s)
	}
	for _, target := range []string{"home_fouls", "away_fouls", "period"} {
		if !errors.Is(a.UpdateGame(target, json.RawMessage("1")), errOCRFollowing) || !errors.Is(a.AdjustScore(target, 1), errOCRFollowing) {
			t.Fatal("manual ownership bypass", target)
		}
	}
	results[4].Text = "31"
	results[5].Text = "30"
	results[6].Text = "0"
	results[2].Text = "11"
	acceptAll(a, results)
	s = a.State()
	if s.HomeFouls != 3 || s.AwayFouls != 30 || s.Period != 4 || s.HomeScore != 11 || !s.PeriodOvertime {
		t.Fatal("per-field rejection or OT changed", s)
	}
	// OT is a separate manual display toggle. OCR only updates the saved number.
	results[6].Text = "5"
	acceptAll(a, results)
	_ = a.UpdateGame("period_overtime", json.RawMessage("false"))
	if a.State().PeriodLabel != "5" || a.State().Period != 5 {
		t.Fatal("saved numeric period lost")
	}
	_ = a.UpdateGame("period_overtime", json.RawMessage("true"))
	ticket := a.ocrTicketLocked()
	_ = a.TakeOCRManual("home_fouls")
	_ = a.TakeOCRManual("period")
	results[4].Text = "1"
	results[5].Text = "7"
	results[6].Text = "6"
	a.acceptOCR(ticket, results, nil, time.Now())
	if a.State().HomeFouls != 3 || a.State().Period != 5 || a.State().AwayFouls != 7 {
		t.Fatal("late takeover crossed ownership")
	}
	cfg, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(cfg, a.path)
	if err != nil {
		t.Fatal(err)
	}
	s = restarted.State()
	if s.HomeFouls != 3 || s.AwayFouls != 7 || s.Period != 5 || s.PeriodLabel != "OT" {
		t.Fatal("restart lost game/OT")
	}
	for _, v := range s.OCR.Targets {
		if v.Following {
			t.Fatal("restart followed")
		}
	}
}

func TestOCRResetAtomicForEveryGameOwner(t *testing.T) {
	for _, owner := range []string{"home_score", "away_score", "home_fouls", "away_fouls", "period"} {
		a := appForTest(t)
		_ = a.UpdateGame("home_score", json.RawMessage("12"))
		_ = a.UpdateGame("away_fouls", json.RawMessage("4"))
		_ = a.UpdateGame("period_overtime", json.RawMessage("true"))
		_ = a.ConnectOCR(defaultScoreSight)
		acceptAll(a, allOCR("05:00", "24", "12", "9"))
		followTarget(t, a, owner)
		before := a.Config()
		if !errors.Is(a.GameReset(), errOCRFollowing) || !reflect.DeepEqual(before, a.Config()) {
			t.Fatal("partial reset", owner)
		}
		_ = a.TakeOCRManual(owner)
		if err := a.GameReset(); err != nil {
			t.Fatal(err)
		}
		s := a.State()
		if s.HomeScore != 0 || s.AwayScore != 0 || s.HomeFouls != 0 || s.AwayFouls != 0 || s.Period != 1 || s.PeriodOvertime {
			t.Fatal("manual reset failed")
		}
	}
}
