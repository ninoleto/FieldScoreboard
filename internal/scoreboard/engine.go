package scoreboard

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"
)

type ClockState struct {
	Display          string  `json:"display"`
	State            string  `json:"state"`
	Direction        string  `json:"direction"`
	DurationSeconds  int     `json:"duration_seconds"`
	RemainingSeconds float64 `json:"remaining_seconds"`
}
type Snapshot struct {
	Version         string      `json:"version"`
	HomeName        string      `json:"home_name"`
	AwayName        string      `json:"away_name"`
	HomeScore       int         `json:"home_score"`
	AwayScore       int         `json:"away_score"`
	HomeFouls       int         `json:"home_fouls"`
	AwayFouls       int         `json:"away_fouls"`
	Period          int         `json:"period"`
	PeriodOvertime  bool        `json:"period_overtime"`
	PeriodLabel     string      `json:"period_label"`
	ShotAutoHide    bool        `json:"shot_auto_hide"`
	ShotVisible     bool        `json:"shot_visible"`
	ActiveListen    string      `json:"active_listen"`
	RestartRequired bool        `json:"restart_required"`
	Main            ClockState  `json:"main"`
	Shot            ClockState  `json:"shot"`
	Layout          Layout      `json:"layout"`
	Listen          string      `json:"listen"`
	OCR             OCRSnapshot `json:"ocr"`
}
type App struct {
	mu           sync.Mutex
	cfg          Config
	path         string
	activeListen string
	main         Clock
	shot         Clock
	ocr          ocrRuntime
	ocrWake      chan struct{}
	ocrLoopOnce  sync.Once
}

func NewApp(cfg Config, path string) (*App, error) {
	if err := ValidateConfig(cfg); err != nil {
		return nil, err
	}
	return &App{cfg: cfg, path: path, activeListen: cfg.Listen, main: newClock(cfg.MainDuration, cfg.MainDirection), shot: newClock(cfg.ShotDuration, "down"), ocr: newOCRRuntime(cfg.OCR), ocrWake: make(chan struct{}, 1)}, nil
}
func cloneLayout(l Layout) Layout {
	if l.BackgroundTransform != nil {
		transform := *l.BackgroundTransform
		l.BackgroundTransform = &transform
	}
	m := make(map[string]Element, len(l.Elements))
	for k, v := range l.Elements {
		m[k] = v
	}
	l.Elements = m
	return l
}
func (a *App) State() Snapshot {
	a.mu.Lock()
	defer a.mu.Unlock()
	now := time.Now()
	a.main.settle(now)
	a.shot.settle(now)
	cs := func(c *Clock, format string) ClockState {
		return ClockState{Display: clockDisplay(c.value(now), format, c.Direction), State: c.State, Direction: c.Direction, DurationSeconds: int(c.Duration / time.Second), RemainingSeconds: c.value(now).Seconds()}
	}
	periodLabel := fmt.Sprint(a.cfg.Period)
	if a.cfg.PeriodOvertime {
		periodLabel = "OT"
	}
	// Display control only. The shot clock continues to use its own monotonic
	// clock; changing visibility must never modify a running game timer.
	shotVisible := true
	if a.cfg.ShotAutoHide {
		mainRemaining := a.main.value(now)
		if a.main.Direction == "up" {
			mainRemaining = a.main.Duration - mainRemaining
		}
		if mainRemaining <= 0 || a.shot.value(now) >= mainRemaining {
			shotVisible = false
		}
	}
	main := cs(&a.main, a.cfg.Layout.MainClockFormat)
	if a.ocr.Following {
		main.State = "ocr"
	}
	return Snapshot{Version: Version, HomeName: a.cfg.HomeName, AwayName: a.cfg.AwayName, HomeScore: a.cfg.HomeScore, AwayScore: a.cfg.AwayScore, HomeFouls: a.cfg.HomeFouls, AwayFouls: a.cfg.AwayFouls, Period: a.cfg.Period, PeriodLabel: periodLabel, PeriodOvertime: a.cfg.PeriodOvertime, ShotAutoHide: a.cfg.ShotAutoHide, ShotVisible: shotVisible, Main: main, Shot: cs(&a.shot, a.cfg.Layout.ShotClockFormat), Layout: cloneLayout(a.cfg.Layout), Listen: a.cfg.Listen, ActiveListen: a.activeListen, RestartRequired: a.cfg.Listen != a.activeListen, OCR: a.ocrSnapshotLocked(now)}
}

// RotateToken atomically persists a fresh API token and immediately invalidates
// the previous one. This is intentionally only exposed through a loopback-only
// POST endpoint; no remote caller can retrieve or rotate credentials.
func (a *App) RotateToken() (string, error) {
	fresh := make([]byte, 32)
	if _, err := rand.Read(fresh); err != nil {
		return "", fmt.Errorf("generate fresh API token: %w", err)
	}
	nextToken := hex.EncodeToString(fresh)
	err := a.updateConfig(func(c *Config) error {
		c.Token = nextToken
		return nil
	})
	if err != nil {
		return "", err
	}
	return nextToken, nil
}

// SetActiveListen records the actual bound address at process startup.
// Saved listener changes require restart; never rebind during an active match.
func (a *App) SetActiveListen(listen string) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.activeListen = listen
}

func (a *App) Config() Config {
	a.mu.Lock()
	defer a.mu.Unlock()
	c := a.cfg
	c.Layout = cloneLayout(c.Layout)
	if c.OCR != nil {
		settings := *c.OCR
		c.OCR = &settings
	}
	return c
}
func (a *App) updateConfig(fn func(*Config) error) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	c := a.cfg
	c.Layout = cloneLayout(c.Layout)
	if err := fn(&c); err != nil {
		return err
	}
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	return nil
}
func (a *App) UpdateGame(field string, value json.RawMessage) error {
	return a.updateConfig(func(c *Config) error {
		switch field {
		case "home_name", "away_name":
			var n string
			if err := json.Unmarshal(value, &n); err != nil {
				return err
			}
			n = strings.TrimSpace(n)
			if n == "" {
				return errors.New("team name cannot be empty")
			}
			if field == "home_name" {
				c.HomeName = n
			} else {
				c.AwayName = n
			}
		case "period_overtime", "shot_auto_hide":
			var enabled bool
			if err := json.Unmarshal(value, &enabled); err != nil {
				return err
			}
			if field == "period_overtime" {
				c.PeriodOvertime = enabled
			} else {
				c.ShotAutoHide = enabled
			}
		case "period", "home_score", "away_score", "home_fouls", "away_fouls":
			var n int
			if err := json.Unmarshal(value, &n); err != nil {
				return err
			}
			switch field {
			case "period":
				c.Period = n
			case "home_score":
				c.HomeScore = n
			case "away_score":
				c.AwayScore = n
			case "home_fouls":
				c.HomeFouls = n
			case "away_fouls":
				c.AwayFouls = n
			}
		default:
			return errors.New("unsupported scoreboard field")
		}
		return nil
	})
}
func (a *App) AdjustScore(field string, delta int) error {
	if delta < -50 || delta > 50 || delta == 0 {
		return errors.New("adjustment must be -50 to +50, nonzero")
	}
	return a.updateConfig(func(c *Config) error {
		switch field {
		case "home_score":
			c.HomeScore += delta
		case "away_score":
			c.AwayScore += delta
		case "home_fouls":
			c.HomeFouls += delta
		case "away_fouls":
			c.AwayFouls += delta
		case "period":
			c.Period += delta
		default:
			return errors.New("unknown field")
		}
		return nil
	})
}
func (a *App) GameReset() error {
	return a.updateConfig(func(c *Config) error {
		c.HomeScore = 0
		c.AwayScore = 0
		c.HomeFouls = 0
		c.AwayFouls = 0
		c.Period = 1
		c.PeriodOvertime = false
		return nil
	})
}
func (a *App) SetClock(which string, seconds int, dir string) error {
	if which != "main" && which != "shot" {
		return errors.New("unknown clock")
	}
	if which == "shot" && dir != "down" {
		return errors.New("shot clock only counts down")
	}
	if seconds < 1 || seconds > 7*86400 || (which == "shot" && seconds > 3600) {
		return errors.New("invalid clock duration")
	}
	return a.updateConfigWithClock(which, seconds, dir)
}
func (a *App) updateConfigWithClock(which string, seconds int, dir string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if which == "main" && a.ocr.Following {
		return errOCRFollowing
	}
	c := a.cfg
	if which == "main" {
		c.MainDuration = seconds
		c.MainDirection = dir
	} else {
		c.ShotDuration = seconds
	}
	if err := saveConfig(a.path, c); err != nil {
		return err
	}
	a.cfg = c
	if which == "main" {
		return a.main.Set(seconds, dir)
	}
	if err := a.shot.Set(seconds, "down"); err != nil {
		return err
	}
	// Setting a new shot-clock duration is also a possession reset. When the
	// match clock is running, immediately count down from the new duration.
	// This does not affect the main clock or automatically link subsequent
	// independent Pause/Stop commands.
	a.resumeShotWithMatchLocked(time.Now())
	return nil
}

// resumeShotWithMatchLocked is called only with a.mu held, immediately after
// Reset/Set of the shot clock. The two clocks are otherwise independent.
func (a *App) resumeShotWithMatchLocked(now time.Time) {
	a.main.settle(now)
	if a.main.State == "running" {
		a.shot.Anchor = now
		a.shot.State = "running"
	}
}

func (a *App) ClockAction(which, action string) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.ocr.Following && (which == "main" || which == "both") {
		return errOCRFollowing
	}
	if which == "both" {
		if action == "pause" || action == "stop" {
			for _, c := range []*Clock{&a.main, &a.shot} {
				if c.State == "running" {
					_ = c.Command(action)
				}
			}
			return nil
		}
		if action != "start" && action != "reset" {
			return errors.New("unknown clock action")
		}
		if err := a.main.Command(action); err != nil {
			return err
		}
		return a.shot.Command(action)
	}
	if which == "main" {
		return a.main.Command(action)
	}
	if which == "shot" {
		if action == "reset" {
			a.shot.Reset()
			a.resumeShotWithMatchLocked(time.Now())
			return nil
		}
		return a.shot.Command(action)
	}
	return errors.New("unknown clock")
}
func (a *App) AdjustClock(which string, seconds int) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if which == "main" && a.ocr.Following {
		return errOCRFollowing
	}
	if which == "main" {
		return a.main.Adjust(seconds)
	}
	if which == "shot" {
		return a.shot.Adjust(seconds)
	}
	return errors.New("unknown clock")
}
func (a *App) UpdateLayout(layout Layout) error {
	return a.updateConfig(func(c *Config) error { c.Layout = cloneLayout(layout); return nil })
}
func (a *App) UpdateListen(listen string) error {
	return a.updateConfig(func(c *Config) error { c.Listen = listen; return nil })
}

var profileName = regexp.MustCompile(`^[A-Za-z0-9][A-Za-z0-9 _-]{0,49}$`)

func (a *App) profilePath(name string) (string, error) {
	name = strings.TrimSpace(name)
	if !profileName.MatchString(name) || strings.Contains(name, "..") {
		return "", errors.New("profile name must use letters, digits, spaces, dashes or underscores")
	}
	return filepath.Join(filepath.Dir(a.path), "profiles", name+".json"), nil
}
func (a *App) SaveProfile(name string) error {
	path, err := a.profilePath(name)
	if err != nil {
		return err
	}
	l := a.State().Layout
	b, err := json.MarshalIndent(l, "", "  ")
	if err != nil {
		return err
	}
	return writeAtomic(path, append(b, '\n'))
}
func (a *App) LoadProfile(name string) error {
	path, err := a.profilePath(name)
	if err != nil {
		return err
	}
	b, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	var l Layout
	if err = json.Unmarshal(b, &l); err != nil {
		return err
	}
	return a.UpdateLayout(l)
}
func (a *App) RemoveProfile(name string) error {
	path, err := a.profilePath(name)
	if err != nil {
		return err
	}
	return os.Remove(path)
}
func (a *App) Profiles() ([]string, error) {
	dir := filepath.Join(filepath.Dir(a.path), "profiles")
	files, err := os.ReadDir(dir)
	if errors.Is(err, os.ErrNotExist) {
		return []string{}, nil
	}
	if err != nil {
		return nil, err
	}
	out := []string{}
	for _, f := range files {
		if !f.IsDir() && strings.HasSuffix(f.Name(), ".json") {
			n := strings.TrimSuffix(f.Name(), ".json")
			if profileName.MatchString(n) {
				out = append(out, n)
			}
		}
	}
	sort.Strings(out)
	return out, nil
}
func (a *App) SetBackground(ref string) error {
	if !validBackground(ref) {
		return fmt.Errorf("invalid background filename")
	}
	var transform *BackgroundTransform
	if ref != "" {
		data, err := os.ReadFile(filepath.Join(filepath.Dir(a.path), "backgrounds", ref))
		if err != nil {
			return err
		}
		w, h, err := backgroundDimensions(data, strings.TrimPrefix(filepath.Ext(ref), "."))
		if err != nil {
			return err
		}
		transform = fitBackground(w, h)
	}
	return a.updateConfig(func(c *Config) error { c.Layout.Background = ref; c.Layout.BackgroundTransform = transform; return nil })
}
func (a *App) ConfigDir() string { return filepath.Dir(a.path) }
