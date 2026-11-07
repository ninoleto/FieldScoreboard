package scoreboard

import (
	"fmt"
	"reflect"
	"testing"
	"time"
)

// The operator shortcuts use the existing adjustment action, not Set/reset.
func TestFourQuickAdjustmentsKeepIndependentClockState(t *testing.T) {
	for _, target := range []string{"main", "shot"} {
		for _, direction := range []string{"down", "up"} {
			if target == "shot" && direction == "up" {
				continue
			}
			for _, state := range []string{"running", "paused"} {
				for _, delta := range []int{-5, -1, 1, 5} {
					t.Run(fmt.Sprintf("%s/%s/%s/%d", target, direction, state, delta), func(t *testing.T) {
						a := appForTest(t)
						clock, other := &a.main, &a.shot
						if target == "shot" {
							clock, other = &a.shot, &a.main
						}
						clock.Direction = direction
						clock.State = state
						clock.Base = 60 * time.Second
						clock.Anchor = time.Now()
						other.State = "running"
						other.Anchor = time.Now()
						before, untouched, cfg := *clock, *other, a.Config()
						if err := a.AdjustClock(target, delta); err != nil {
							t.Fatal(err)
						}
						now := time.Now()
						if clock.value(now) != before.value(now)+time.Duration(delta)*time.Second || clock.State != state {
							t.Fatal("adjustment changed transport or wrong delta", *clock)
						}
						if *other != untouched || !reflect.DeepEqual(cfg, a.Config()) {
							t.Fatal("adjustment changed other clock or settings")
						}
					})
				}
			}
		}
	}
}

func TestQuickAdjustmentBoundariesAndOCROwnership(t *testing.T) {
	for _, target := range []string{"main", "shot"} {
		a := appForTest(t)
		clock := &a.main
		if target == "shot" {
			clock = &a.shot
		}
		for _, state := range []string{"running", "paused"} {
			for _, delta := range []int{-5, -1} {
				clock.State = state
				clock.Base = 0
				clock.Anchor = time.Now()
				if err := a.AdjustClock(target, delta); err != nil || clock.Base != 0 || clock.State != "completed" {
					t.Fatal("countdown zero", target, state, delta, err, *clock)
				}
			}
			for _, delta := range []int{1, 5} {
				clock.State = state
				clock.Base = 7 * 24 * time.Hour
				clock.Anchor = time.Now()
				before := *clock
				if a.AdjustClock(target, delta) == nil || *clock != before {
					t.Fatal("upper rejection mutated clock", target, state, delta)
				}
				clock.State = "paused"
				clock.Base = 7*24*time.Hour - time.Duration(delta)*time.Second
				if err := a.AdjustClock(target, delta); err != nil || clock.Base != 7*24*time.Hour || clock.State != "paused" {
					t.Fatal("exact upper bound", err)
				}
			}
		}
		if target == "main" {
			clock.Direction = "up"
			clock.State = "paused"
			clock.Base = 0
			if err := a.AdjustClock(target, -5); err != nil || clock.Base != 0 || clock.State != "paused" {
				t.Fatal("count-up zero", err)
			}
		}
		_ = a.ConnectOCR(defaultScoreSight)
		acceptAll(a, allOCR("05:00", "24", "9", "8"))
		followTarget(t, a, target)
		before := *clock
		srv, err := NewServer(a)
		if err != nil {
			t.Fatal(err)
		}
		for _, delta := range []int{-5, -1, 1, 5} {
			w := apiCall(t, srv.Handler(), "/api/clock/"+target+"/adjust", "POST", fmt.Sprintf(`{"seconds":%d}`, delta), false, "")
			if w.Code != 400 || *clock != before {
				t.Fatal("OCR guard", target, delta, w.Code, w.Body)
			}
		}
	}
}
