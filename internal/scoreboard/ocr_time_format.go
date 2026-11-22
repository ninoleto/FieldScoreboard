package scoreboard

import (
	"errors"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// Optional OCR presentation preferences live outside Layout and profiles.
type OCRTimeFormatSettings struct {
	Enabled           bool   `json:"enabled"`
	FinalMinuteFormat string `json:"final_minute_format"`
	FinalMinuteStyle  string `json:"final_minute_style,omitempty"`
}

func (s OCRTimeFormatSettings) validate() error {
	if s.FinalMinuteFormat != "" && s.FinalMinuteFormat != "SS" && s.FinalMinuteFormat != "SS.t" {
		return errors.New("final minute format must be SS or SS.t")
	}
	if s.FinalMinuteStyle != "" && s.FinalMinuteStyle != "visible" && s.FinalMinuteStyle != "invisible" && s.FinalMinuteStyle != "clean" {
		return errors.New("final minute style must be visible, invisible or clean")
	}
	return nil
}

func (a *App) ocrTimeFormatLocked() OCRTimeFormatSettings {
	s := OCRTimeFormatSettings{FinalMinuteFormat: "SS", FinalMinuteStyle: "clean"}
	if a.cfg.OCR != nil && a.cfg.OCR.MainTimeFormat != nil {
		s = *a.cfg.OCR.MainTimeFormat
		if s.FinalMinuteFormat == "" {
			s.FinalMinuteFormat = "SS"
		}
		if s.FinalMinuteStyle == "" {
			s.FinalMinuteStyle = "clean"
		}
	}
	return s
}

func (a *App) SetOCRTimeFormat(s OCRTimeFormatSettings) error {
	if s.FinalMinuteFormat == "" {
		return errors.New("final minute format must be SS or SS.t")
	}
	if err := s.validate(); err != nil {
		return err
	}
	a.mu.Lock()
	defer a.mu.Unlock()
	previous := a.ocrTimeFormatLocked()
	// Older clients omit the new presentation field; retain the chosen style.
	if s.FinalMinuteStyle == "" {
		s.FinalMinuteStyle = previous.FinalMinuteStyle
	}
	settings := a.ocrSettingsLocked()
	settings.MainTimeFormat = &s
	// Presentation never changes recognition, ownership or in-flight revisions.
	return a.saveOCRSettingsLocked(settings)
}

// Keep integer game values and exact clock durations distinct. No float
// conversion or independent clock ticks are involved in OCR observations.
type ocrValue struct {
	number int
	clock  time.Duration
}

var ocrFinalMinutePattern = regexp.MustCompile(`^[0-5]?[0-9](\.[0-9])?$`)

func parseOCRObservation(target, text string) (ocrValue, error) {
	if target == "main" && !strings.Contains(text, ":") {
		if !ocrFinalMinutePattern.MatchString(text) {
			return ocrValue{}, errors.New("expected MM:SS or final-minute SS / SS.t (0–59.9)")
		}
		parts := strings.Split(text, ".")
		seconds, _ := strconv.Atoi(parts[0])
		value := time.Duration(seconds) * time.Second
		if len(parts) == 2 {
			value += time.Duration(parts[1][0]-'0') * 100 * time.Millisecond
		}
		return ocrValue{clock: value}, nil
	}
	value, err := parseOCRValue(target, text)
	if target == "main" || target == "shot" {
		return ocrValue{clock: time.Duration(value) * time.Second}, err
	}
	return ocrValue{number: value}, err
}

func (a *App) mainClockDisplayLocked(now time.Time) string {
	v := a.main.value(now)
	s := a.ocrTimeFormatLocked()
	if a.ocrFollowingLocked("main") && s.Enabled {
		format := "MM:SS"
		if v < time.Minute {
			format = s.FinalMinuteFormat
		}
		// Omit tenths instead of rounding an authoritative 59.9 up to 60.
		// Manual countdown rounding remains unchanged in clockDisplay.
		display := clockDisplay(v, format, "up")
		if v < time.Minute {
			switch s.FinalMinuteStyle {
			case "visible":
				display = "00:" + display
			case "invisible":
				display = ":" + display
			}
		}
		return display
	}
	return clockDisplay(v, a.cfg.Layout.MainClockFormat, a.main.Direction)
}
