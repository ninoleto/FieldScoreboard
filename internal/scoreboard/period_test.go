package scoreboard

import (
	"encoding/json"
	"reflect"
	"strconv"
	"strings"
	"testing"
)

func TestPeriodFormatsAndOCRNormalization(t *testing.T) {
	ordinals := []string{"1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "13th", "14th", "15th", "16th", "17th", "18th", "19th", "20th"}
	for i, ordinal := range ordinals {
		n := i + 1
		number := strconv.Itoa(n)
		for format, want := range map[string]string{"number": number, "ordinal": ordinal, "quarter": "Q" + number} {
			if got := periodDisplay(n, format); got != want {
				t.Fatalf("%d %s: %s != %s", n, format, got, want)
			}
			for _, raw := range []string{want, strings.ToUpper(want), strings.ToLower(want), " \t" + want + "\n "} {
				if value, err := parseOCRValue("period", raw); err != nil || value != n {
					t.Fatalf("%q: %d %v", raw, value, err)
				}
			}
		}
	}
	for _, raw := range []string{"03", "03rd", "q03"} {
		if n, err := parseOCRPeriod(raw); err != nil || n != 3 {
			t.Fatal("leading-zero compatibility", raw, n, err)
		}
	}
	for _, raw := range []string{"", " ", "0", "00", "Q0", "0th", "21", "Q21", "21st", "100", "1th", "2rd", "3th", "4rd", "11st", "12nd", "13rd", "Q3rd", "Quarter 3", "Period 3", "3rd quarter", "Q 3", "3 rd", "3.0", "+3", "-3", "3/4", "3\nrd", "３", "3rd!", "OT", "003"} {
		if _, err := parseOCRPeriod(raw); err == nil || !strings.Contains(err.Error(), "valid ordinal") {
			t.Fatal("invalid period accepted or unclear validation", raw, err)
		}
	}
	for _, target := range []string{"home_score", "away_score", "home_fouls", "away_fouls", "shot"} {
		for _, raw := range []string{"3rd", "Q3", " 3 "} {
			if _, err := parseOCRValue(target, raw); err == nil {
				t.Fatal("changed other target parser", target, raw)
			}
		}
	}
}

func TestPeriodFormatStatePersistenceAndOwnership(t *testing.T) {
	a := appForTest(t)
	if s := a.State(); s.PeriodFormat != "number" || s.PeriodLabel != "1" {
		t.Fatal("legacy default", s)
	}
	set := func(field string, value any) {
		t.Helper()
		raw, _ := json.Marshal(value)
		if err := a.UpdateGame(field, raw); err != nil {
			t.Fatal(field, err)
		}
	}
	for _, format := range []string{"number", "ordinal", "quarter"} {
		set("period_format", format)
		set("period", 11)
		if err := a.AdjustScore("period", 1); err != nil {
			t.Fatal(err)
		}
		if s := a.State(); s.Period != 12 || s.PeriodLabel != periodDisplay(12, format) {
			t.Fatal(s)
		}
		set("period_overtime", true)
		cfg, err := LoadOrCreate(a.path)
		if err != nil {
			t.Fatal(err)
		}
		a, err = NewApp(cfg, a.path)
		if err != nil {
			t.Fatal(err)
		}
		if s := a.State(); s.PeriodFormat != format || s.Period != 12 || s.PeriodLabel != "OT" {
			t.Fatal("restart", s)
		}
		set("period_overtime", false)
		if a.State().PeriodLabel != periodDisplay(12, format) {
			t.Fatal("OT restore")
		}
	}
	before := a.Config()
	for _, raw := range []string{`""`, `"roman"`, `"Number"`, `3`, `null`, `true`, `"3rd"`} {
		if a.UpdateGame("period_format", json.RawMessage(raw)) == nil || !reflect.DeepEqual(before, a.Config()) {
			t.Fatal("invalid format changed settings", raw)
		}
	}
	if err := a.SaveProfile("period-test"); err != nil {
		t.Fatal(err)
	}
	set("period_format", "ordinal")
	set("period", 13)
	if err := a.LoadProfile("period-test"); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.PeriodFormat != "ordinal" || s.Period != 13 {
		t.Fatal("preset replaced live settings", s)
	}
	_ = a.ConnectOCR(defaultScoreSight)
	results := allOCR("05:00", "24", "9", "8")
	results[6].Text = " 3rD "
	acceptAll(a, results)
	followTarget(t, a, "period")
	beforeFollow := a.State()
	for _, format := range []string{"number", "ordinal", "quarter"} {
		set("period_format", format)
		s := a.State()
		o := s.OCR.Targets["period"]
		if s.Period != 3 || s.PeriodLabel != periodDisplay(3, format) || !o.Following || o.Recognized != " 3rD " || o.LastAccepted != "3" {
			t.Fatal(s)
		}
		if s.Main != beforeFollow.Main || s.Shot != beforeFollow.Shot || s.HomeScore != beforeFollow.HomeScore || !reflect.DeepEqual(s.Layout, beforeFollow.Layout) {
			t.Fatal("format changed unrelated state")
		}
	}
	set("period_overtime", true)
	results[6].Text = "Q13"
	acceptAll(a, results)
	if s := a.State(); s.Period != 13 || s.PeriodLabel != "OT" || !s.PeriodOvertime {
		t.Fatal(s)
	}
	set("period_overtime", false)
	if a.State().PeriodLabel != "Q13" {
		t.Fatal("OCR OT restore")
	}
	for _, raw := range []string{"3th", "Q21", "period 2"} {
		results[6].Text = raw
		acceptAll(a, results)
		s := a.State()
		o := s.OCR.Targets["period"]
		if s.Period != 13 || o.LastAccepted != "13" || o.Recognized != raw || o.Reading != "malformed" {
			t.Fatal("invalid did not hold", s)
		}
	}
	results[6].Text = "2nd"
	results[6].State = "FailedFilter"
	acceptAll(a, results)
	if a.State().Period != 13 || a.State().OCR.Targets["period"].Reading != "rejected" {
		t.Fatal("rejected status applied")
	}
	acceptAll(a, results[:6])
	if a.State().Period != 13 {
		t.Fatal("missing cleared period")
	}
	_ = a.TakeOCRManual("period")
	if err := a.GameReset(); err != nil {
		t.Fatal(err)
	}
	if s := a.State(); s.Period != 1 || s.PeriodFormat != "quarter" || s.PeriodLabel != "Q1" {
		t.Fatal("reset lost format", s)
	}
	cfg := a.Config()
	cfg.PeriodFormat = "invalid"
	if ValidateConfig(cfg) == nil {
		t.Fatal("invalid persisted format allowed")
	}
}
