package scoreboard

import (
	"encoding/json"
	"math"
	"reflect"
	"strings"
	"testing"
)

func TestElementTransformValidationLegacyAndPersistence(t *testing.T) {
	a := appForTest(t)
	legacy := a.State().Layout
	data, _ := json.Marshal(legacy)
	if strings.Contains(string(data), `"transform"`) {
		t.Fatal("legacy transform unexpectedly added")
	}
	for _, id := range FieldIDs {
		l := cloneLayout(legacy)
		el := l.Elements[id]
		el.Transform = &ElementTransform{ScaleX: 1.5, ScaleY: 2, LockAspect: false}
		l.Elements[id] = el
		if err := a.UpdateLayout(l); err != nil {
			t.Fatal(id, err)
		}
		s := a.State()
		s.Layout.Elements[id].Transform.ScaleX = 9
		c := a.Config()
		c.Layout.Elements[id].Transform.ScaleY = 9
		if a.State().Layout.Elements[id].Transform.ScaleX != 1.5 || a.State().Layout.Elements[id].Transform.ScaleY != 2 {
			t.Fatal("transform alias escaped mutex")
		}
		cfg, err := LoadOrCreate(a.path)
		if err != nil {
			t.Fatal(err)
		}
		restarted, err := NewApp(cfg, a.path)
		if err != nil || !reflect.DeepEqual(restarted.State().Layout, l) {
			t.Fatal("transform restart", id, err)
		}
	}
	for _, value := range []float64{0, -1, .049, 20.001, math.NaN(), math.Inf(1)} {
		l := cloneLayout(legacy)
		el := l.Elements["home_score"]
		el.Transform = &ElementTransform{ScaleX: value, ScaleY: 1}
		l.Elements["home_score"] = el
		if ValidateLayout(l) == nil {
			t.Fatal("invalid transform", value)
		}
	}
	for _, value := range []float64{.05, 1, 20} {
		l := cloneLayout(legacy)
		el := l.Elements["home_fouls"]
		el.Transform = &ElementTransform{ScaleX: value, ScaleY: value, LockAspect: true}
		l.Elements["home_fouls"] = el
		if err := ValidateLayout(l); err != nil {
			t.Fatal(value, err)
		}
	}
}
