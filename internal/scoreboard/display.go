package scoreboard

import (
	"encoding/json"
	"errors"
)

// Keep the existing layout/preset representation. Live changes patch one
// preference without touching geometry, clocks, game values or OCR ownership.
func (a *App) UpdateDisplay(field string, value json.RawMessage) error {
	return a.updateConfig(func(c *Config) error {
		if field == "foul_dots_max" {
			var n int
			if err := json.Unmarshal(value, &n); err != nil {
				return err
			}
			c.Layout.FoulDotsMax = n
			return nil
		}
		var v string
		if err := json.Unmarshal(value, &v); err != nil {
			return err
		}
		switch field {
		case "foul_style_home":
			c.Layout.FoulStyleHome = v
		case "foul_style_away":
			c.Layout.FoulStyleAway = v
		case "main_clock_format":
			c.Layout.MainClockFormat = v
		case "shot_clock_format":
			c.Layout.ShotClockFormat = v
		default:
			return errors.New("unknown display preference")
		}
		return nil
	})
}

// The editor owns geometry/styling drafts, not these immediate preferences.
// Merge under the configuration mutex so even a delayed Save cannot roll back
// a newer display change. Legacy full-layout APIs and presets stay compatible.
func (a *App) UpdateEditorLayout(layout Layout) error {
	return a.updateConfig(func(c *Config) error {
		layout.FoulStyleHome = c.Layout.FoulStyleHome
		layout.FoulStyleAway = c.Layout.FoulStyleAway
		layout.FoulDotsMax = c.Layout.FoulDotsMax
		layout.MainClockFormat = c.Layout.MainClockFormat
		layout.ShotClockFormat = c.Layout.ShotClockFormat
		c.Layout = cloneLayout(layout)
		return nil
	})
}
