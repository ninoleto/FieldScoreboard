package scoreboard

import (
	"io"
	"net/http/httptest"
	"strings"
	"testing"
)

type trackedActionBody struct {
	io.Reader
	eof bool
}

func (b *trackedActionBody) Read(p []byte) (int, error) {
	n, err := b.Reader.Read(p)
	if err == io.EOF {
		b.eof = true
	}
	return n, err
}
func (b *trackedActionBody) Close() error { return nil }
func TestActionBodyConsumedBeforeResponseAndMutation(t *testing.T) {
	for _, route := range []string{"/api/clock/main/reset", "/api/reset-game", "/api/token/rotate"} {
		a := appForTest(t)
		s, _ := NewServer(a)
		body := &trackedActionBody{Reader: strings.NewReader(`{}`)}
		r := httptest.NewRequest("POST", route, nil)
		r.RemoteAddr = "127.0.0.1:1234"
		r.Header.Set("Content-Type", "application/json")
		r.Body = body
		r.ContentLength = 2
		w := httptest.NewRecorder()
		s.Handler().ServeHTTP(w, r)
		if w.Code != 200 || !body.eof {
			t.Fatal("action left unread data", route, w.Code, body.eof)
		}
		before := a.Config()
		r = httptest.NewRequest("POST", route, strings.NewReader(strings.Repeat("x", 65537)))
		r.RemoteAddr = "127.0.0.1:1234"
		r.Header.Set("Content-Type", "application/json")
		w = httptest.NewRecorder()
		s.Handler().ServeHTTP(w, r)
		if w.Code != 413 || a.Config().Token != before.Token {
			t.Fatal("unbounded body / side effect", route, w.Code)
		}
	}
}
