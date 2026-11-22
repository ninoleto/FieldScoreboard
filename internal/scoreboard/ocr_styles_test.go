package scoreboard

import (
	"encoding/json"
	"reflect"
	"testing"
	"time"
)

func TestOCRTimeFormatStyles(t *testing.T) {
	for _, style := range []string{"visible", "invisible", "clean"} {
		for _, format := range []string{"SS", "SS.t"} {
			t.Run(style+"/"+format, func(t *testing.T) {
				a := appForTest(t)
				a.UpdateDisplay("main_clock_format", json.RawMessage(`"HH:MM:SS"`))
				preference := OCRTimeFormatSettings{Enabled: true, FinalMinuteFormat: format, FinalMinuteStyle: style}
				if err := a.SetOCRTimeFormat(preference); err != nil {
					t.Fatal(err)
				}
				if err := a.ConnectOCR(defaultScoreSight); err != nil {
					t.Fatal(err)
				}
				acceptAll(a, allOCR("01:05", "24", "7", "8"))
				followTarget(t, a, "main")
				before := a.Config()
				for _, step := range []struct {
					raw, whole, tenth string
					value             float64
				}{
					{"01:05", "01:05", "01:05", 65}, {"01:00", "01:00", "01:00", 60},
					{"59.9", "59", "59.9", 59.9}, {"32.5", "32", "32.5", 32.5},
					{"5.0", "05", "05.0", 5}, {"0.0", "00", "00.0", 0},
					{"20:00", "20:00", "20:00", 1200},
				} {
					injectOCR(a, step.raw, "Success", time.Now())
					want := step.whole
					if format == "SS.t" {
						want = step.tenth
					}
					if step.value < 60 {
						if style == "visible" {
							want = "00:" + want
						}
						if style == "invisible" {
							want = ":" + want
						}
					}
					state := a.State()
					if state.Main.Display != want || state.Main.RemainingSeconds != step.value || state.Main.DisplayStyle != style || state.Main.DisplayTenths != (format == "SS.t") {
						t.Fatal(step, state.Main)
					}
					srv, _ := NewServer(a)
					if srv.overlayState().Main != state.Main {
						t.Fatal("overlay presentation differs")
					}
				}
				if !reflect.DeepEqual(before, a.Config()) {
					t.Fatal("observations persisted configuration")
				}
				// Style/precision changes do not invalidate observations or ownership.
				injectOCR(a, "32.5", "Success", time.Now())
				a.mu.Lock()
				revision := a.ocr.targets["main"].revision
				a.mu.Unlock()
				preference.FinalMinuteStyle = "invisible"
				if err := a.SetOCRTimeFormat(preference); err != nil {
					t.Fatal(err)
				}
				a.mu.Lock()
				changed := a.ocr.targets["main"].revision != revision
				a.mu.Unlock()
				if changed || !a.State().OCR.Following || a.State().Main.RemainingSeconds != 32.5 {
					t.Fatal("presentation changed ownership/precision/revision")
				}
				// Omitted style from a .1 client retains the new preference.
				if err := a.SetOCRTimeFormat(OCRTimeFormatSettings{Enabled: true, FinalMinuteFormat: format}); err != nil {
					t.Fatal(err)
				}
				if a.State().OCR.MainTimeFormat.FinalMinuteStyle != "invisible" {
					t.Fatal("legacy API overwrote style")
				}
				a.DisconnectOCR()
				if state := a.State(); state.Main.Display != "00:00:33" || state.Main.DisplayStyle != "" || state.Main.DisplayTenths || state.Main.RemainingSeconds != 32.5 {
					t.Fatal("manual restoration", state.Main)
				}
				cfg, err := LoadOrCreate(a.path)
				if err != nil {
					t.Fatal(err)
				}
				restarted, err := NewApp(cfg, a.path)
				if err != nil {
					t.Fatal(err)
				}
				if state := restarted.State(); state.OCR.MainTimeFormat.FinalMinuteStyle != "invisible" || state.Main.DisplayStyle != "" || state.OCR.Following {
					t.Fatal("restart", state.Main, state.OCR)
				}
			})
		}
	}
}

func TestOCRTimeFormatStyleValidation(t *testing.T) {
	a := appForTest(t)
	before := a.Config()
	if err := a.SetOCRTimeFormat(OCRTimeFormatSettings{Enabled: true, FinalMinuteFormat: "SS", FinalMinuteStyle: "spaces"}); err == nil {
		t.Fatal("invalid style accepted")
	}
	if !reflect.DeepEqual(before, a.Config()) {
		t.Fatal("invalid style mutated config")
	}
	legacy := before
	legacy.OCR = &OCRSettings{Address: defaultScoreSight, MainTimeFormat: &OCRTimeFormatSettings{Enabled: true, FinalMinuteFormat: "SS.t"}}
	b, err := NewApp(legacy, a.path)
	if err != nil || b.State().OCR.MainTimeFormat.FinalMinuteStyle != "clean" {
		t.Fatal("legacy style default", err)
	}
	legacy.OCR.MainTimeFormat.FinalMinuteStyle = "invalid"
	if _, err := NewApp(legacy, a.path); err == nil {
		t.Fatal("invalid config style accepted")
	}
}
