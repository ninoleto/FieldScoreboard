package scoreboard

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"math"
	"net"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

const Version = "0.1.0-test.14"
const CanvasW = 1920
const CanvasH = 1080

var FieldIDs = []string{"period", "main_clock", "shot_clock", "home_score", "away_score", "home_fouls", "away_fouls", "home_name", "away_name"}

// ElementTransform scales rendered content, not a fixed clipping rectangle.
// Nil is the exact legacy output. Dynamic values keep the same scale/anchor.
type ElementTransform struct {
	ScaleX     float64 `json:"scale_x"`
	ScaleY     float64 `json:"scale_y"`
	LockAspect bool    `json:"lock_aspect"`
}
type Element struct {
	Transform *ElementTransform `json:"transform,omitempty"`
	X         int               `json:"x"`
	Y         int               `json:"y"`
	Font      string            `json:"font"`
	Size      int               `json:"size"`
	Color     string            `json:"color"`
	Bold      bool              `json:"bold"`
	Align     string            `json:"align"`
	Visible   bool              `json:"visible"`
}
type Layout struct {
	Elements            map[string]Element   `json:"elements"`
	Background          string               `json:"background"` // only internal sha256 filename or empty
	BackgroundTransform *BackgroundTransform `json:"background_transform,omitempty"`
	FoulStyleHome       string               `json:"foul_style_home"`
	FoulStyleAway       string               `json:"foul_style_away"`
	FoulDotsMax         int                  `json:"foul_dots_max"`
	MainClockFormat     string               `json:"main_clock_format"`
	ShotClockFormat     string               `json:"shot_clock_format"`
}
type Config struct {
	Version        int          `json:"version"`
	Listen         string       `json:"listen"`
	Token          string       `json:"token"`
	HomeName       string       `json:"home_name"`
	AwayName       string       `json:"away_name"`
	HomeScore      int          `json:"home_score"`
	AwayScore      int          `json:"away_score"`
	HomeFouls      int          `json:"home_fouls"`
	AwayFouls      int          `json:"away_fouls"`
	Period         int          `json:"period"`
	PeriodFormat   string       `json:"period_format,omitempty"`
	PeriodOvertime bool         `json:"period_overtime"`
	ShotAutoHide   bool         `json:"shot_auto_hide"`
	MainDuration   int          `json:"main_duration"`
	ShotDuration   int          `json:"shot_duration"`
	MainDirection  string       `json:"main_direction"`
	Layout         Layout       `json:"layout"`
	OCR            *OCRSettings `json:"ocr,omitempty"`
}

func DefaultLayout() Layout {
	elements := map[string]Element{}
	placements := map[string][3]int{
		"period": {95, 62, 54}, "main_clock": {305, 52, 70}, "shot_clock": {670, 62, 54},
		"home_name": {920, 74, 50}, "home_score": {1175, 49, 90}, "away_score": {1400, 49, 90}, "away_name": {1625, 74, 50},
		"home_fouls": {1135, 175, 32}, "away_fouls": {1390, 175, 32},
	}
	for _, id := range FieldIDs {
		p := placements[id]
		col := "#ffffff"
		if id == "shot_clock" {
			col = "#ffba59"
		}
		if strings.Contains(id, "fouls") {
			col = "#ffcd67"
		}
		elements[id] = Element{X: p[0], Y: p[1], Size: p[2], Color: col, Font: "sans", Bold: true, Align: "left", Visible: true}
	}
	return Layout{Elements: elements, FoulStyleHome: "dots", FoulStyleAway: "dots", FoulDotsMax: 5, MainClockFormat: "MM:SS", ShotClockFormat: "SS"}
}
func DefaultConfig() (Config, error) {
	b := make([]byte, 32)
	if _, err := rand.Read(b); err != nil {
		return Config{}, err
	}
	return Config{Version: 1, Listen: "127.0.0.1:8790", Token: hex.EncodeToString(b), HomeName: "HOME", AwayName: "AWAY", Period: 1, MainDuration: 1200, ShotDuration: 24, MainDirection: "down", Layout: DefaultLayout()}, nil
}
func ConfigPath() (string, error) {
	d, e := os.UserConfigDir()
	if e != nil {
		return "", e
	}
	return filepath.Join(d, "FieldScoreboard", "config.json"), nil
}
func writeAtomic(path string, b []byte) error {
	d := filepath.Dir(path)
	if err := os.MkdirAll(d, 0700); err != nil {
		return err
	}
	f, err := os.CreateTemp(d, ".scoreboard-*.tmp")
	if err != nil {
		return err
	}
	defer os.Remove(f.Name())
	if err = f.Chmod(0600); err != nil {
		f.Close()
		return err
	}
	if _, err = f.Write(b); err != nil {
		f.Close()
		return err
	}
	if err = f.Close(); err != nil {
		return err
	}
	return os.Rename(f.Name(), path)
}
func saveConfig(path string, c Config) error {
	if err := ValidateConfig(c); err != nil {
		return err
	}
	b, err := json.MarshalIndent(c, "", "  ")
	if err != nil {
		return err
	}
	return writeAtomic(path, append(b, '\n'))
}
func LoadOrCreate(path string) (Config, error) {
	b, err := os.ReadFile(path)
	if errors.Is(err, os.ErrNotExist) {
		c, e := DefaultConfig()
		if e != nil {
			return c, e
		}
		return c, saveConfig(path, c)
	}
	if err != nil {
		return Config{}, err
	}
	var c Config
	if err = json.Unmarshal(b, &c); err != nil {
		return c, err
	}
	if err = ValidateConfig(c); err != nil {
		return c, fmt.Errorf("invalid configuration: %w", err)
	}
	return c, nil
}
func validColor(s string) bool {
	if len(s) != 7 || s[0] != '#' {
		return false
	}
	_, err := hex.DecodeString(s[1:])
	return err == nil
}
func validBackground(s string) bool {
	if s == "" {
		return true
	}
	x := strings.Split(s, ".")
	if len(x) != 2 || len(x[0]) != 64 {
		return false
	}
	if _, err := hex.DecodeString(x[0]); err != nil {
		return false
	}
	return x[1] == "png" || x[1] == "jpg" || x[1] == "webp"
}
func ValidateLayout(l Layout) error {
	if l.FoulStyleHome != "dots" && l.FoulStyleHome != "number" {
		return errors.New("invalid home foul style")
	}
	if l.FoulStyleAway != "dots" && l.FoulStyleAway != "number" {
		return errors.New("invalid away foul style")
	}
	if l.FoulDotsMax < 1 || l.FoulDotsMax > 20 {
		return errors.New("foul dots maximum must be 1–20")
	}
	if l.MainClockFormat != "MM:SS" && l.MainClockFormat != "M:SS" && l.MainClockFormat != "HH:MM:SS" && l.MainClockFormat != "SS" && l.MainClockFormat != "MM:SS.t" {
		return errors.New("invalid main clock format")
	}
	if l.ShotClockFormat != "SS" && l.ShotClockFormat != "SS.t" && l.ShotClockFormat != "MM:SS" {
		return errors.New("invalid shot clock format")
	}
	if !validBackground(l.Background) {
		return errors.New("invalid background reference")
	}
	if err := validateBackgroundTransform(l.BackgroundTransform); err != nil {
		return err
	}
	if l.Background == "" && l.BackgroundTransform != nil {
		return errors.New("background transform requires an image")
	}
	if len(l.Elements) != len(FieldIDs) {
		return errors.New("layout must contain all nine fields")
	}
	for _, id := range FieldIDs {
		el, ok := l.Elements[id]
		if !ok {
			return fmt.Errorf("missing field %s", id)
		}
		if el.X < 0 || el.X > CanvasW || el.Y < 0 || el.Y > CanvasH {
			return fmt.Errorf("invalid position for %s", id)
		}
		if el.Transform != nil {
			for _, scale := range []float64{el.Transform.ScaleX, el.Transform.ScaleY} {
				if math.IsNaN(scale) || math.IsInf(scale, 0) || scale < .05 || scale > 20 {
					return fmt.Errorf("invalid transform for %s", id)
				}
			}
		}
		if el.Size < 12 || el.Size > 240 {
			return fmt.Errorf("invalid font size for %s", id)
		}
		if el.Font != "mono" && el.Font != "sans" && el.Font != "serif" && el.Font != "heavy" {
			return fmt.Errorf("invalid font for %s", id)
		}
		if el.Align != "left" && el.Align != "center" && el.Align != "right" {
			return fmt.Errorf("invalid alignment for %s", id)
		}
		if !validColor(el.Color) {
			return fmt.Errorf("invalid color for %s", id)
		}
	}
	return nil
}
func ValidateConfig(c Config) error {
	if c.OCR != nil {
		if _, err := normalizeScoreSight(c.OCR.Address); err != nil {
			return err
		}
		for target, field := range c.OCR.Mappings {
			if _, ok := ocrSuggestions[target]; !ok || !validOCRField(field) {
				return errors.New("invalid OCR mapping")
			}
		}
		if !validOCRField(c.OCR.Field) {
			return errors.New("invalid OCR field name")
		}
	}
	if c.Version != 1 {
		return errors.New("unsupported config version")
	}
	if c.Listen == "" {
		return errors.New("listen address required")
	}
	host, port, err := net.SplitHostPort(c.Listen)
	if err != nil || port == "" || host == "" {
		return errors.New("invalid listen host:port")
	}
	portNumber, portErr := strconv.Atoi(port)
	if portErr != nil || portNumber < 1024 || portNumber > 65535 {
		return errors.New("listen port must be between 1024 and 65535")
	}
	if host != "localhost" {
		if ip := net.ParseIP(host); ip == nil {
			return errors.New("listen must be an IP or localhost")
		}
	}
	if len(c.Token) != 64 {
		return errors.New("invalid token")
	}
	if _, err = hex.DecodeString(c.Token); err != nil {
		return errors.New("invalid token")
	}
	if len([]rune(c.HomeName)) > 32 || len([]rune(c.AwayName)) > 32 {
		return errors.New("team names too long")
	}
	if c.HomeScore < 0 || c.HomeScore > 999 || c.AwayScore < 0 || c.AwayScore > 999 {
		return errors.New("scores out of range")
	}
	if c.HomeFouls < 0 || c.HomeFouls > 30 || c.AwayFouls < 0 || c.AwayFouls > 30 {
		return errors.New("fouls out of range")
	}
	if c.Period < 1 || c.Period > 20 {
		return errors.New("period out of range")
	}
	// Missing settings in earlier configurations retain numeric presentation.
	if c.PeriodFormat != "" && !validPeriodFormat(c.PeriodFormat) {
		return errors.New("period format must be number, ordinal or quarter")
	}
	if c.MainDuration < 1 || c.MainDuration > 7*86400 || c.ShotDuration < 1 || c.ShotDuration > 3600 {
		return errors.New("clock duration out of range")
	}
	if c.MainDirection != "up" && c.MainDirection != "down" {
		return errors.New("main clock direction must be up/down")
	}
	return ValidateLayout(c.Layout)
}

// Clock has a monotonic anchor. Runtime clock state never resumes automatically after restart.
type Clock struct {
	Duration  time.Duration
	Direction string
	State     string
	Base      time.Duration
	Anchor    time.Time
}

func newClock(sec int, dir string) Clock {
	c := Clock{Duration: time.Duration(sec) * time.Second, Direction: dir, State: "ready"}
	c.Reset()
	return c
}
func (c *Clock) Reset() {
	c.State = "ready"
	if c.Direction == "up" {
		c.Base = 0
	} else {
		c.Base = c.Duration
	}
	c.Anchor = time.Time{}
}
func (c *Clock) value(now time.Time) time.Duration {
	v := c.Base
	if c.State == "running" {
		span := now.Sub(c.Anchor)
		if c.Direction == "down" {
			v -= span
		} else {
			v += span
		}
	}
	if c.Direction == "down" && v < 0 {
		return 0
	}
	return v
}
func (c *Clock) settle(now time.Time) {
	if c.Direction == "down" && c.State == "running" && c.value(now) <= 0 {
		c.Base = 0
		c.State = "completed"
		c.Anchor = time.Time{}
	}
}
func (c *Clock) Command(action string) error {
	now := time.Now()
	c.settle(now)
	switch action {
	case "start":
		if c.State == "running" {
			return nil
		}
		if c.State == "stopped" || c.State == "completed" {
			c.Reset()
		}
		c.Anchor = now
		c.State = "running"
	case "pause":
		if c.State != "running" {
			return errors.New("clock is not running")
		}
		c.Base = c.value(now)
		c.Anchor = time.Time{}
		c.State = "paused"
	case "stop":
		if c.State == "running" {
			c.Base = c.value(now)
		}
		c.Anchor = time.Time{}
		c.State = "stopped"
	case "reset":
		c.Reset()
	default:
		return fmt.Errorf("unknown clock action %q", action)
	}
	return nil
}
func (c *Clock) Set(seconds int, dir string) error {
	if seconds < 1 || seconds > 7*86400 {
		return errors.New("duration out of range")
	}
	if dir != "up" && dir != "down" {
		return errors.New("direction must be up or down")
	}
	c.Duration = time.Duration(seconds) * time.Second
	c.Direction = dir
	c.Reset()
	return nil
}
func (c *Clock) Adjust(deltaSeconds int) error {
	now := time.Now()
	c.settle(now)
	if deltaSeconds < -7*86400 || deltaSeconds > 7*86400 {
		return errors.New("adjustment out of range")
	}
	v := c.value(now) + time.Duration(deltaSeconds)*time.Second
	if v < 0 {
		v = 0
	}
	if v > 7*24*time.Hour {
		return errors.New("adjusted clock exceeds seven days")
	}
	c.Base = v
	if c.State == "running" {
		c.Anchor = now
	}
	if c.Direction == "down" && v == 0 {
		c.State = "completed"
		c.Anchor = time.Time{}
	}
	return nil
}
func clockDisplay(v time.Duration, format string, dir string) string {
	var total int64
	if dir == "down" {
		total = int64((v + time.Second - 1) / time.Second)
	} else {
		total = int64(v / time.Second)
	}
	if total < 0 {
		total = 0
	}
	switch format {
	case "SS":
		return fmt.Sprintf("%02d", total)
	case "SS.t", "MM:SS.t":
		tenths := int64(v / (100 * time.Millisecond))
		if dir == "down" && v > 0 {
			tenths = int64((v + 100*time.Millisecond - 1) / (100 * time.Millisecond))
		}
		if tenths < 0 {
			tenths = 0
		}
		if format == "SS.t" {
			return fmt.Sprintf("%02d.%d", tenths/10, tenths%10)
		}
		return fmt.Sprintf("%02d:%02d.%d", tenths/600, (tenths/10)%60, tenths%10)
	case "M:SS":
		return fmt.Sprintf("%d:%02d", total/60, total%60)
	case "HH:MM:SS":
		return fmt.Sprintf("%02d:%02d:%02d", total/3600, (total/60)%60, total%60)
	default:
		return fmt.Sprintf("%02d:%02d", total/60, total%60)
	}
}
