package scoreboard

import (
	"encoding/json"
	"errors"
	"testing"
	"time"
)

func TestOCRRecognitionIndependentOfOutput(t *testing.T) {
	formats := []struct{ format, down, up string }{
		{"MM:SS", "00:49", "00:48"}, {"M:SS", "0:49", "0:48"},
		{"HH:MM:SS", "00:00:49", "00:00:48"}, {"SS", "49", "48"},
		{"MM:SS.t", "00:48.2", "00:48.2"},
	}
	for _, f := range formats {
		for _, direction := range []string{"down", "up"} {
			t.Run(f.format+"/"+direction, func(t *testing.T) {
				a := appForTest(t)
				if err := a.SetClock("main", 1200, direction); err != nil {
					t.Fatal(err)
				}
				value, _ := json.Marshal(f.format)
				if err := a.UpdateDisplay("main_clock_format", value); err != nil {
					t.Fatal(err)
				}
				if err := a.ConnectOCR(defaultScoreSight); err != nil {
					t.Fatal(err)
				}
				before := a.State().Main
				acceptAll(a, allOCR("48.2", "24", "7", "8"))
				if s := a.State(); !s.OCR.CanFollow || s.OCR.Following || s.Main != before {
					t.Fatal("decimal must be available to follow without taking control", s.Main, s.OCR)
				}
				followTarget(t, a, "main")
				manual := f.down
				if direction == "up" {
					manual = f.up
				}
				for _, enabled := range []bool{false, true, false} {
					for _, precision := range []string{"SS", "SS.t"} {
						for _, style := range []string{"visible", "invisible", "clean"} {
							ticket := a.ocrTicketLocked()
							if err := a.SetOCRTimeFormat(OCRTimeFormatSettings{Enabled: enabled, FinalMinuteFormat: precision, FinalMinuteStyle: style}); err != nil {
								t.Fatal(err)
							}
							if a.ocrTicketLocked().revisions["main"] != ticket.revisions["main"] {
								t.Fatal("presentation invalidated observation")
							}
							// A valid in-flight response must survive a presentation change.
							a.acceptOCR(ticket, allOCR("48.2", "24", "7", "8"), nil, time.Now())
							want := manual
							if enabled {
								want = "48"
								if precision == "SS.t" {
									want = "48.2"
								}
								if style == "visible" {
									want = "00:" + want
								}
								if style == "invisible" {
									want = ":" + want
								}
							}
							s := a.State()
							if s.Main.RemainingSeconds != 48.2 || s.Main.Display != want || !s.OCR.Following || s.OCR.LastAccepted != "48.2" {
								t.Fatal(enabled, precision, style, s.Main, s.OCR)
							}
							if a.main.value(time.Now().Add(time.Hour)) != 48200*time.Millisecond {
								t.Fatal("OCR ticked independently")
							}
							if s.Layout.MainClockFormat != f.format {
								t.Fatal("manual format overwritten")
							}
							srv, _ := NewServer(a)
							if srv.overlayState().Main != s.Main {
								t.Fatal("overlay differs")
							}
							for _, bad := range []string{"48.22", "00:48.2", ":48.2", "60.0", " 48.2", "time 48.2"} {
								injectOCR(a, bad, "Success", time.Now())
								if a.State().Main != s.Main || a.State().OCR.Reading != "malformed" {
									t.Fatal("invalid reading did not hold", bad)
								}
							}
							a.acceptOCR(a.ocrTicketLocked(), nil, errors.New("source loss"), time.Now())
							if a.State().Main != s.Main || !a.State().OCR.Following {
								t.Fatal("source loss changed value/ownership")
							}
							injectOCR(a, "48.2", "SameNoChange", time.Now())
						}
					}
				}
				ticket := a.ocrTicketLocked()
				a.TakeManualControl()
				a.acceptOCR(ticket, allOCR("20:00", "24", "7", "8"), nil, time.Now())
				if s := a.State(); s.Main.RemainingSeconds != 48.2 || s.Main.Display != manual || s.Main.State != "paused" || s.OCR.Following {
					t.Fatal("takeover/late response", s.Main)
				}
			})
		}
	}
}
