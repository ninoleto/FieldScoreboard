package scoreboard

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"sync/atomic"
	"testing"
	"time"
)

func TestOCRDisconnectRetainsAllValuesAndRejectsOldConnection(t *testing.T) {
	a := appForTest(t)
	if err := a.ConnectOCR(defaultScoreSight); err != nil {
		t.Fatal(err)
	}
	results := []scoreSightResult{}
	for target, text := range map[string]string{"main": "03:21", "shot": "14", "home_score": "35", "away_score": "27", "home_fouls": "4", "away_fouls": "2", "period": "3rd"} {
		results = append(results, scoreSightResult{Name: ocrSuggestions[target], Text: text, State: "Success"})
	}
	a.acceptOCR(a.ocrTicketLocked(), results, nil, time.Now())
	for _, target := range ocrTargets {
		if err := a.FollowOCRTarget(target); err != nil {
			t.Fatal(err)
		}
	}
	settings, before, ticket := a.ocrSettingsLocked(), a.State(), a.ocrTicketLocked()
	a.DisconnectOCR()
	assertHeld := func() {
		t.Helper()
		s := a.State()
		if s.Main.Display != before.Main.Display || s.Shot.Display != before.Shot.Display || s.Main.State != "paused" || s.Shot.State != "paused" || s.HomeScore != before.HomeScore || s.AwayScore != before.AwayScore || s.HomeFouls != before.HomeFouls || s.AwayFouls != before.AwayFouls || s.Period != before.Period {
			t.Fatal("disconnect/reconnect lost values or started clocks", s)
		}
		for _, view := range s.OCR.Targets {
			if view.Following {
				t.Fatal("ownership resumed")
			}
		}
		if !reflect.DeepEqual(settings, a.ocrSettingsLocked()) {
			t.Fatal("settings changed")
		}
	}
	assertHeld()
	if a.State().OCR.Connection != "disconnected" || a.State().OCR.Monitoring {
		t.Fatal("still monitoring")
	}
	for _, target := range ocrTargets {
		if a.FollowOCRTarget(target) == nil {
			t.Fatal("follow accepted while disconnected")
		}
	}
	for i := range results {
		results[i].Text = "0"
	}
	// Both successful and failed late responses must be ignored after disconnect,
	// including after a new connection has been established.
	for _, reconnect := range []bool{false, true} {
		if reconnect {
			if err := a.ConnectOCR(defaultScoreSight); err != nil {
				t.Fatal(err)
			}
		}
		a.acceptOCR(ticket, results, nil, time.Now())
		a.acceptOCR(ticket, nil, errors.New("late failure"), time.Now())
		assertHeld()
		if a.State().OCR.Connection == "error" {
			t.Fatal("old failure changed new status")
		}
	}
	results = []scoreSightResult{{Name: "Time", Text: "01:11", State: "Success"}}
	a.acceptOCR(a.ocrTicketLocked(), results, nil, time.Now())
	assertHeld()
	if err := a.FollowOCR(); err != nil {
		t.Fatal(err)
	}
	if a.State().Main.Display != "01:11" || a.State().Main.State != "ocr" {
		t.Fatal("explicit following failed")
	}
}

func TestOCRConnectIdempotentAndExplicitRetryManual(t *testing.T) {
	a := appForTest(t)
	_ = a.ConnectOCR(defaultScoreSight)
	generation := a.ocr.generation
	for i := 0; i < 10; i++ {
		if err := a.ConnectOCR(defaultScoreSight); err != nil {
			t.Fatal(err)
		}
	}
	if a.ocr.generation != generation {
		t.Fatal("pending connect restarted")
	}
	injectOCR(a, "04:00", "Success", time.Now())
	_ = a.FollowOCR()
	if err := a.ConnectOCR(defaultScoreSight); err != nil {
		t.Fatal(err)
	}
	if a.ocr.generation != generation || !a.State().OCR.Following {
		t.Fatal("duplicate connect changed active ownership")
	}
	if a.ConnectOCR("http://127.0.0.1:18098") == nil {
		t.Fatal("changed active address")
	}
	a.acceptOCR(a.ocrTicketLocked(), nil, errors.New("lost"), time.Now())
	if err := a.ConnectOCR(defaultScoreSight); err != nil {
		t.Fatal(err)
	}
	if a.State().OCR.Following || a.State().Main.State != "paused" || a.State().Main.Display != "04:00" {
		t.Fatal("retry resumed ownership or lost time")
	}
	// Disconnect must leave independent manual clocks alone.
	_ = a.ClockAction("shot", "start")
	a.DisconnectOCR()
	if a.State().Shot.State != "running" {
		t.Fatal("disconnect changed unrelated manual clock")
	}
}

func TestOCRDisconnectCancelsRequestAndStopsPolling(t *testing.T) {
	var calls atomic.Int32
	entered, canceled := make(chan struct{}), make(chan struct{})
	source := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if calls.Add(1) == 1 {
			close(entered)
			<-r.Context().Done()
			close(canceled)
			return
		}
		fmt.Fprint(w, `[{"name":"Time","text":"02:22","state":"Success"}]`)
	}))
	defer source.Close()
	a := appForTest(t)
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go a.RunOCR(ctx)
	_ = a.ConnectOCR(source.URL)
	select {
	case <-entered:
	case <-time.After(3 * time.Second):
		t.Fatal("no request")
	}
	a.DisconnectOCR()
	select {
	case <-canceled:
	case <-time.After(500 * time.Millisecond):
		t.Fatal("request was not canceled immediately")
	}
	time.Sleep(3 * ocrPollInterval)
	if calls.Load() != 1 || a.State().OCR.Connection != "disconnected" {
		t.Fatal("polling continued after disconnect", calls.Load())
	}
	_ = a.ConnectOCR(source.URL)
	deadline := time.Now().Add(3 * time.Second)
	for !a.State().OCR.CanFollow && time.Now().Before(deadline) {
		time.Sleep(10 * time.Millisecond)
	}
	if !a.State().OCR.CanFollow || a.State().OCR.Following || a.State().Main.State != "ready" {
		t.Fatal("reconnect failed or started clock")
	}
	a.DisconnectOCR()
}
