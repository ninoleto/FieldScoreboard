package scoreboard

import (
	"context"
	"crypto/sha256"
	"crypto/subtle"
	"embed"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"mime"
	"net"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

//go:embed web/*
var webFS embed.FS

type Server struct {
	App    *App
	assets http.Handler
}

func NewServer(a *App) (*Server, error) {
	f, err := fs.Sub(webFS, "web")
	if err != nil {
		return nil, err
	}
	return &Server{App: a, assets: http.FileServer(http.FS(f))}, nil
}
func loopback(r *http.Request) bool {
	h, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return false
	}
	ip := net.ParseIP(h)
	return ip != nil && ip.IsLoopback()
}
func (s *Server) allowed(r *http.Request) bool {
	if loopback(r) {
		return true
	}
	auth := r.Header.Get("Authorization")
	token := s.App.Config().Token
	expected := "Bearer " + token
	return subtle.ConstantTimeCompare([]byte(auth), []byte(expected)) == 1
}
func apiErr(w http.ResponseWriter, code int, message string) {
	respond(w, code, map[string]string{"error": message})
}
func respond(w http.ResponseWriter, code int, data any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(code)
	_ = json.NewEncoder(w).Encode(data)
}
func decode(r *http.Request, into any) error {
	if !strings.HasPrefix(r.Header.Get("Content-Type"), "application/json") {
		return errors.New("Content-Type must be application/json")
	}
	dec := json.NewDecoder(io.LimitReader(r.Body, 65537))
	dec.DisallowUnknownFields()
	if err := dec.Decode(into); err != nil {
		return err
	}
	var extra any
	if err := dec.Decode(&extra); !errors.Is(err, io.EOF) {
		return errors.New("exactly one JSON object is required")
	}
	return nil
}

// Bodyless action endpoints historically accept an optional unused body. Drain
// it before replying: closing HTTP/1 connections with unread bytes can reset a
// large response on Windows. Keep reads bounded and do not change API semantics.
func consumeActionBody(w http.ResponseWriter, r *http.Request) bool {
	if r.Body == nil || r.Body == http.NoBody {
		return true
	}
	controller := http.NewResponseController(w)
	_ = controller.SetReadDeadline(time.Now().Add(5 * time.Second))
	defer controller.SetReadDeadline(time.Time{})
	_, err := io.Copy(io.Discard, http.MaxBytesReader(w, r.Body, 65536))
	if err != nil {
		var tooLarge *http.MaxBytesError
		if errors.As(err, &tooLarge) {
			apiErr(w, 413, "action body too large")
		} else {
			apiErr(w, 400, "incomplete action body")
		}
		return false
	}
	return true
}

// overlayAllowed permits local OBS, or read-only OBS clients on trusted
// private networks ONLY after LAN listening was applied by a restart.
// Remote clients never receive an API token or access to control endpoints.
func (s *Server) overlayAllowed(r *http.Request) bool {
	if loopback(r) {
		return true
	}
	host, _, err := net.SplitHostPort(s.App.State().ActiveListen)
	if err != nil || host != "0.0.0.0" {
		return false
	}
	remoteHost, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return false
	}
	return isUsablePrivateIPv4(net.ParseIP(remoteHost))
}

// Only data used by the OBS overlay is exposed without authentication.
// No listener, restart metadata, configuration token or network adapters.
type publicOverlayState struct {
	HomeName    string     `json:"home_name"`
	AwayName    string     `json:"away_name"`
	HomeScore   int        `json:"home_score"`
	AwayScore   int        `json:"away_score"`
	HomeFouls   int        `json:"home_fouls"`
	AwayFouls   int        `json:"away_fouls"`
	Period      int        `json:"period"`
	PeriodLabel string     `json:"period_label"`
	ShotVisible bool       `json:"shot_visible"`
	Main        ClockState `json:"main"`
	Shot        ClockState `json:"shot"`
	Layout      Layout     `json:"layout"`
}

func (s *Server) overlayState() publicOverlayState {
	st := s.App.State()
	return publicOverlayState{
		HomeName: st.HomeName, AwayName: st.AwayName,
		HomeScore: st.HomeScore, AwayScore: st.AwayScore,
		HomeFouls: st.HomeFouls, AwayFouls: st.AwayFouls,
		Period: st.Period, PeriodLabel: st.PeriodLabel,
		ShotVisible: st.ShotVisible, Main: st.Main, Shot: st.Shot,
		Layout: st.Layout,
	}
}

func (s *Server) Handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/api/", s.api)
	mux.HandleFunc("/overlay", s.overlayStatic("/overlay.html"))
	mux.HandleFunc("/overlay.html", s.overlayStatic("/overlay.html"))
	mux.HandleFunc("/overlay.js", s.overlayStatic("/overlay.js"))
	mux.HandleFunc("/overlay.css", s.overlayStatic("/overlay.css"))
	mux.HandleFunc("/background/", s.background)
	mux.Handle("/", s.assets)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("X-Content-Type-Options", "nosniff")
		w.Header().Set("Referrer-Policy", "no-referrer")
		w.Header().Set("X-Frame-Options", "DENY")
		w.Header().Set("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data: blob:; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
		if r.URL.Path == "/overlay" || strings.HasPrefix(r.URL.Path, "/overlay.") {
			w.Header().Set("Cache-Control", "no-store")
		}
		mux.ServeHTTP(w, r)
	})
}
func (s *Server) overlayStatic(path string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		if !s.overlayAllowed(r) {
			apiErr(w, 403, "remote OBS requires LAN access and a trusted private IP")
			return
		}
		r2 := r.Clone(r.Context())
		r2.URL.Path = path
		s.assets.ServeHTTP(w, r2)
	}
}
func (s *Server) background(w http.ResponseWriter, r *http.Request) {
	name := strings.TrimPrefix(r.URL.Path, "/background/")
	if r.Method != http.MethodGet || !validBackground(name) || name == "" {
		http.NotFound(w, r)
		return
	}
	p := filepath.Join(s.App.ConfigDir(), "backgrounds", name)
	w.Header().Set("Cache-Control", "private, max-age=3600")
	if strings.HasSuffix(name, ".png") {
		w.Header().Set("Content-Type", "image/png")
	} else if strings.HasSuffix(name, ".webp") {
		w.Header().Set("Content-Type", "image/webp")
	} else {
		w.Header().Set("Content-Type", "image/jpeg")
	}
	http.ServeFile(w, r, p)
}
func (s *Server) api(w http.ResponseWriter, r *http.Request) {
	p := strings.TrimPrefix(r.URL.Path, "/api/")
	if p == "health" && r.Method == "GET" {
		respond(w, 200, map[string]string{"name": "Field Scoreboard", "version": Version})
		return
	}
	if p == "events" && r.Method == "GET" {
		if !loopback(r) {
			apiErr(w, 403, "events are local-only")
			return
		}
		s.events(w, r, false)
		return
	}
	if (p == "overlay-state" || p == "overlay-events") && r.Method == "GET" {
		if !s.overlayAllowed(r) {
			apiErr(w, 403, "remote OBS requires LAN access and a trusted private IP")
			return
		}
		if p == "overlay-events" {
			s.events(w, r, true)
		} else {
			respond(w, 200, s.overlayState())
		}
		return
	}
	if p == "network-interfaces" && r.Method == "GET" {
		if !loopback(r) {
			apiErr(w, 403, "network interfaces are host-only")
			return
		}
		respond(w, 200, detectNetworkInterfaces())
		return
	}
	if p == "token" && r.Method == "GET" {
		if !loopback(r) {
			apiErr(w, 403, "token is host-only")
			return
		}
		respond(w, 200, map[string]string{"token": s.App.Config().Token})
		return
	}
	if p == "token/rotate" && r.Method == "POST" {
		// Require JSON content type to prevent cross-site HTML form requests
		// from rotating tokens on localhost without a CORS preflight.
		if !strings.HasPrefix(r.Header.Get("Content-Type"), "application/json") {
			apiErr(w, 415, "Content-Type must be application/json")
			return
		}
		if !loopback(r) {
			apiErr(w, 403, "API token rotation is host-only")
			return
		}
		if !consumeActionBody(w, r) {
			return
		}
		fresh, err := s.App.RotateToken()
		if err != nil {
			apiErr(w, 500, "unable to rotate API token")
			return
		}
		respond(w, 200, map[string]string{"token": fresh})
		return
	}
	if !s.allowed(r) {
		apiErr(w, 401, "API token required for remote access")
		return
	}
	switch {
	case p == "ocr/connect" && r.Method == "POST":
		var v struct {
			Address string `json:"address"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		s.done(w, s.App.ConnectOCR(v.Address))
	case p == "ocr/field" && r.Method == "POST":
		var v struct {
			Field  string `json:"field"`
			Target string `json:"target"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		if v.Target == "" {
			v.Target = "main"
		}
		s.done(w, s.App.SelectOCRMapping(v.Target, v.Field))
	case (p == "ocr/follow" || p == "ocr/manual") && r.Method == "POST":
		var v struct {
			Target string `json:"target"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		if v.Target == "" {
			v.Target = "main"
		}
		if p == "ocr/follow" {
			s.done(w, s.App.FollowOCRTarget(v.Target))
		} else {
			s.done(w, s.App.TakeOCRManual(v.Target))
		}
	case p == "state" && r.Method == "GET":
		respond(w, 200, s.App.State())
	case p == "profiles" && r.Method == "GET":
		names, err := s.App.Profiles()
		if err != nil {
			apiErr(w, 500, err.Error())
			return
		}
		respond(w, 200, map[string]any{"profiles": names})
	case p == "profiles" && r.Method == "POST":
		var v struct {
			Name   string `json:"name"`
			Action string `json:"action"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		var err error
		switch v.Action {
		case "save":
			err = s.App.SaveProfile(v.Name)
		case "load":
			err = s.App.LoadProfile(v.Name)
		case "delete":
			err = s.App.RemoveProfile(v.Name)
		default:
			err = errors.New("unknown profile action")
		}
		s.done(w, err)
	case p == "game" && r.Method == "POST":
		var v struct {
			Field string          `json:"field"`
			Value json.RawMessage `json:"value"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		s.done(w, s.App.UpdateGame(v.Field, v.Value))
	case p == "adjust" && r.Method == "POST":
		var v struct {
			Field string `json:"field"`
			Delta int    `json:"delta"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		s.done(w, s.App.AdjustScore(v.Field, v.Delta))
	case p == "reset-game" && r.Method == "POST":
		if !consumeActionBody(w, r) {
			return
		}
		s.done(w, s.App.GameReset())
	case strings.HasPrefix(p, "clock/") && r.Method == "POST":
		parts := strings.Split(p, "/")
		if len(parts) != 3 {
			apiErr(w, 404, "unknown clock endpoint")
			return
		}
		which, action := parts[1], parts[2]
		if action == "set" {
			var v struct {
				Seconds   int    `json:"seconds"`
				Direction string `json:"direction"`
			}
			if err := decode(r, &v); err != nil {
				apiErr(w, 400, err.Error())
				return
			}
			if v.Direction == "" {
				v.Direction = "down"
			}
			s.done(w, s.App.SetClock(which, v.Seconds, v.Direction))
			return
		}
		if action == "adjust" {
			var v struct {
				Seconds int `json:"seconds"`
			}
			if err := decode(r, &v); err != nil {
				apiErr(w, 400, err.Error())
				return
			}
			s.done(w, s.App.AdjustClock(which, v.Seconds))
			return
		}
		if !consumeActionBody(w, r) {
			return
		}
		s.done(w, s.App.ClockAction(which, action))
	case p == "layout" && r.Method == "PUT":
		var v Layout
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		s.done(w, s.App.UpdateLayout(v))
	case p == "network" && r.Method == "PUT":
		var v struct {
			Listen string `json:"listen"`
		}
		if err := decode(r, &v); err != nil {
			apiErr(w, 400, err.Error())
			return
		}
		s.done(w, s.App.UpdateListen(v.Listen))
	case p == "background" && r.Method == "POST":
		s.uploadBackground(w, r)
	case p == "background" && r.Method == "DELETE":
		s.done(w, s.App.SetBackground(""))
	default:
		apiErr(w, 404, "unknown API method or route")
	}
}
func (s *Server) done(w http.ResponseWriter, err error) {
	if err != nil {
		apiErr(w, 400, err.Error())
		return
	}
	respond(w, 200, s.App.State())
}
func (s *Server) uploadBackground(w http.ResponseWriter, r *http.Request) {
	const max = 15 << 20
	r.Body = http.MaxBytesReader(w, r.Body, max+1)
	data, err := io.ReadAll(r.Body)
	if err != nil {
		apiErr(w, 413, "background exceeds 15 MB")
		return
	}
	if len(data) == 0 || len(data) > max {
		apiErr(w, 413, "background must be 1 byte to 15 MB")
		return
	}
	mimeType := http.DetectContentType(data[:min(len(data), 512)])
	ext := ""
	switch mimeType {
	case "image/png":
		ext = "png"
	case "image/jpeg":
		ext = "jpg"
	case "image/webp":
		ext = "webp"
	default:
		apiErr(w, 415, "only PNG, JPEG and WebP are supported")
		return
	}
	width, height, err := backgroundDimensions(data, ext)
	if err != nil {
		apiErr(w, 400, err.Error())
		return
	}
	h := sha256.Sum256(data)
	ref := hex.EncodeToString(h[:]) + "." + ext
	dest := filepath.Join(s.App.ConfigDir(), "backgrounds", ref)
	if _, err = os.Stat(dest); errors.Is(err, os.ErrNotExist) {
		if err = writeAtomic(dest, data); err != nil {
			apiErr(w, 500, err.Error())
			return
		}
	} else if err != nil {
		apiErr(w, 500, err.Error())
		return
	}
	// Existing callers still import immediately. The editor stages its upload
	// until Save layout, so Discard can restore the entire previous graphic.
	if r.URL.Query().Get("draft") != "1" {
		if err = s.App.SetBackground(ref); err != nil {
			apiErr(w, 500, err.Error())
			return
		}
	}
	respond(w, 200, map[string]any{"background": ref, "background_transform": fitBackground(width, height), "url": "/background/" + ref, "state": s.App.State()})
}
func (s *Server) events(w http.ResponseWriter, r *http.Request, overlayOnly bool) {
	fl, ok := w.(http.Flusher)
	if !ok {
		apiErr(w, 500, "streaming unsupported")
		return
	}
	w.Header().Set("Content-Type", "text/event-stream; charset=utf-8")
	w.Header().Set("Cache-Control", "no-cache, no-transform")
	w.Header().Set("Connection", "keep-alive")
	w.Header().Set("X-Accel-Buffering", "no")
	t := time.NewTicker(100 * time.Millisecond)
	defer t.Stop()
	hb := time.NewTicker(10 * time.Second)
	defer hb.Stop()
	prev := ""
	send := func() {
		var b []byte
		if overlayOnly {
			b, _ = json.Marshal(s.overlayState())
		} else {
			b, _ = json.Marshal(s.App.State())
		}
		v := string(b)
		if v != prev {
			prev = v
			_, _ = fmt.Fprintf(w, "data: %s\n\n", v)
			fl.Flush()
		}
	}
	send()
	for {
		select {
		case <-r.Context().Done():
			return
		case <-t.C:
			send()
		case <-hb.C:
			_, _ = io.WriteString(w, ": keepalive\n\n")
			fl.Flush()
		}
	}
}
func HTTPServer(s *Server, listen string) *http.Server {
	return &http.Server{Addr: listen, Handler: s.Handler(), ReadHeaderTimeout: 5 * time.Second, IdleTimeout: 120 * time.Second}
}
func (s *Server) RunClockLoop(ctx context.Context) {
	go s.App.RunOCR(ctx)
	// Background tick ensures expired clocks settle when no overlay client is connected.
	t := time.NewTicker(100 * time.Millisecond)
	defer t.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-t.C:
			s.App.State()
		}
	}
}

// Used by clients to detect a requested listener change that needs a restart.
func ListenerRestartRequired(configured, active string) bool { return configured != active }
func ParsePort(listen string) string {
	_, port, err := net.SplitHostPort(listen)
	if err != nil {
		return "8790"
	}
	if _, err = strconv.Atoi(port); err != nil {
		return "8790"
	}
	return port
}
func ImageMime(ext string) string {
	if t := mime.TypeByExtension("." + ext); t != "" {
		return t
	}
	return "application/octet-stream"
}
