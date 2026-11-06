package scoreboard

import (
	"bytes"
	"encoding/binary"
	"encoding/json"
	"image"
	"image/color"
	"image/jpeg"
	"image/png"
	"math"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func graphicFixture(t *testing.T, w, h int, ext string) []byte {
	t.Helper()
	img := image.NewNRGBA(image.Rect(0, 0, w, h))
	img.SetNRGBA(w/2, h/2, color.NRGBA{R: 220, G: 100, A: 128})
	var data bytes.Buffer
	var err error
	if ext == "jpg" {
		err = jpeg.Encode(&data, img, nil)
	} else {
		err = png.Encode(&data, img)
	}
	if err != nil {
		t.Fatal(err)
	}
	return data.Bytes()
}

func TestBackgroundImportFitAndDraft(t *testing.T) {
	for _, shape := range []struct {
		name string
		w, h int
	}{
		{"square", 400, 400}, {"portrait", 400, 800}, {"banner", 1600, 200}, {"canvas", 1920, 1080},
	} {
		for _, ext := range []string{"png", "jpg"} {
			t.Run(shape.name+"-"+ext, func(t *testing.T) {
				a := appForTest(t)
				server, _ := NewServer(a)
				data := graphicFixture(t, shape.w, shape.h, ext)
				for _, draft := range []bool{true, false} {
					path := "/api/background"
					if draft {
						path += "?draft=1"
					}
					r := httptest.NewRequest("POST", path, bytes.NewReader(data))
					r.RemoteAddr = "127.0.0.1:5000"
					response := httptest.NewRecorder()
					server.Handler().ServeHTTP(response, r)
					if response.Code != 200 {
						t.Fatalf("upload: %d %s", response.Code, response.Body.String())
					}
					var body struct {
						Background string               `json:"background"`
						Transform  *BackgroundTransform `json:"background_transform"`
					}
					if err := json.Unmarshal(response.Body.Bytes(), &body); err != nil {
						t.Fatal(err)
					}
					if body.Transform == nil || body.Transform.Mode != "fit" || !body.Transform.LockAspect {
						t.Fatal("missing fit/lock default")
					}
					tr := body.Transform
					if math.Abs(tr.Width/tr.Height-float64(shape.w)/float64(shape.h)) > 1e-9 {
						t.Fatal("distorted import")
					}
					if tr.Width > CanvasW+.001 || tr.Height > CanvasH+.001 || tr.X != (CanvasW-tr.Width)/2 || tr.Y != (CanvasH-tr.Height)/2 {
						t.Fatal("fit not contained and centered")
					}
					saved, err := os.ReadFile(filepath.Join(a.ConfigDir(), "backgrounds", body.Background))
					if err != nil || !bytes.Equal(saved, data) {
						t.Fatal("original bytes changed")
					}
					if draft {
						if a.State().Layout.Background != "" || a.State().Layout.BackgroundTransform != nil {
							t.Fatal("draft changed live layout")
						}
					} else if a.State().Layout.BackgroundTransform == nil {
						t.Fatal("normal API upload did not select the graphic")
					}
				}
			})
		}
	}
}

func TestBackgroundPersistenceLegacyAndCopies(t *testing.T) {
	a := appForTest(t)
	legacy := a.State().Layout
	legacy.Background = strings.Repeat("a", 64) + ".png"
	if err := a.UpdateLayout(legacy); err != nil {
		t.Fatal(err)
	}
	if err := a.SaveProfile("Legacy"); err != nil {
		t.Fatal(err)
	}
	if a.State().Layout.BackgroundTransform != nil {
		t.Fatal("legacy appearance was migrated")
	}
	l := a.State().Layout
	l.BackgroundTransform = &BackgroundTransform{Mode: "custom", Width: 960, Height: 480, X: -40.5, Y: 275.25, OriginalWidth: 800, OriginalHeight: 400, LockAspect: true}
	if err := a.UpdateLayout(l); err != nil {
		t.Fatal(err)
	}
	l.BackgroundTransform.X = 999
	if a.State().Layout.BackgroundTransform.X != -40.5 {
		t.Fatal("input aliases live transform")
	}
	for _, copy := range []Layout{a.State().Layout, a.Config().Layout} {
		copy.BackgroundTransform.Width = 5
	}
	if a.State().Layout.BackgroundTransform.Width != 960 {
		t.Fatal("snapshot aliases live transform")
	}
	if err := a.SaveProfile("Positioned"); err != nil {
		t.Fatal(err)
	}
	c, err := LoadOrCreate(a.path)
	if err != nil {
		t.Fatal(err)
	}
	restarted, err := NewApp(c, a.path)
	if err != nil {
		t.Fatal(err)
	}
	if tr := restarted.State().Layout.BackgroundTransform; tr == nil || tr.X != -40.5 || tr.Height != 480 || !tr.LockAspect {
		t.Fatal("transform lost on restart")
	}
	if err := a.LoadProfile("Legacy"); err != nil {
		t.Fatal(err)
	}
	if a.State().Layout.BackgroundTransform != nil {
		t.Fatal("legacy preset materialized a transform")
	}
	if err := a.LoadProfile("Positioned"); err != nil {
		t.Fatal(err)
	}
	if a.State().Layout.BackgroundTransform.X != -40.5 {
		t.Fatal("profile lost placement")
	}
	a.SetActiveListen("0.0.0.0:8790")
	server, _ := NewServer(a)
	response := apiCall(t, server.Handler(), "/api/overlay-state", "GET", "", true, "")
	if response.Code != 200 {
		t.Fatal(response.Body.String())
	}
	var overlay publicOverlayState
	if err := json.Unmarshal(response.Body.Bytes(), &overlay); err != nil {
		t.Fatal(err)
	}
	if overlay.Layout.BackgroundTransform.X != -40.5 || strings.Contains(response.Body.String(), "token") {
		t.Fatal("LAN transform missing or secret leaked")
	}
	if err := a.SetBackground(""); err != nil {
		t.Fatal(err)
	}
	if a.State().Layout.BackgroundTransform != nil {
		t.Fatal("remove left transform behind")
	}
}

func TestBackgroundTransformValidation(t *testing.T) {
	base := fitBackground(800, 400)
	for name, alter := range map[string]func(*BackgroundTransform){
		"zero": func(t *BackgroundTransform) { t.Width = 0 }, "negative": func(t *BackgroundTransform) { t.Height = -1 },
		"huge": func(t *BackgroundTransform) { t.X = MaxBackgroundExtent + 1 }, "nan": func(t *BackgroundTransform) { t.Width = math.NaN() },
		"infinity": func(t *BackgroundTransform) { t.Y = math.Inf(1) }, "mode": func(t *BackgroundTransform) { t.Mode = "bogus" },
		"metadata": func(t *BackgroundTransform) { t.OriginalWidth = 0 },
	} {
		t.Run(name, func(t *testing.T) {
			v := *base
			alter(&v)
			if validateBackgroundTransform(&v) == nil {
				t.Fatal("accepted invalid transform")
			}
		})
	}
	for _, mode := range []string{"fit", "fill", "original", "stretch", "custom"} {
		v := *base
		v.Mode = mode
		if err := validateBackgroundTransform(&v); err != nil {
			t.Fatal(err)
		}
	}
	if err := validateBackgroundTransform(fitBackground(8192, 1)); err != nil {
		t.Fatal(err)
	}
}

func webpHeader(chunk string, payload []byte) []byte {
	var b bytes.Buffer
	b.WriteString("RIFF")
	binary.Write(&b, binary.LittleEndian, uint32(12+len(payload)+(len(payload)&1)))
	b.WriteString("WEBP")
	b.WriteString(chunk)
	binary.Write(&b, binary.LittleEndian, uint32(len(payload)))
	b.Write(payload)
	if len(payload)&1 == 1 {
		b.WriteByte(0)
	}
	return b.Bytes()
}
func TestWebPDimensionsAndMalformedHeaders(t *testing.T) {
	// Metadata-only fixtures test bounded header parsing; browser tests use real
	// encoded WebP pixels. No image decoder or external runtime is added to Go.
	bits := uint32(399) | uint32(799)<<14
	lossless := []byte{0x2f, byte(bits), byte(bits >> 8), byte(bits >> 16), byte(bits >> 24)}
	for _, data := range [][]byte{
		webpHeader("VP8L", lossless),
		webpHeader("VP8 ", []byte{0, 0, 0, 0x9d, 1, 0x2a, 0x90, 1, 0x20, 3}),
		webpHeader("VP8X", []byte{0, 0, 0, 0, 0x8f, 1, 0, 0x1f, 3, 0}),
	} {
		w, h, err := backgroundDimensions(data, "webp")
		if err != nil || w != 400 || h != 800 {
			t.Fatalf("WebP: %d %d %v", w, h, err)
		}
		for n := 0; n < len(data); n++ {
			if _, _, err := webpDimensions(data[:n]); err == nil {
				t.Fatalf("accepted truncated header at %d", n)
			}
		}
	}
	bad := webpHeader("VP8X", []byte{0, 0, 0, 0, 0xff, 0xff, 0xff, 1, 1, 1})
	if _, _, err := backgroundDimensions(bad, "webp"); err == nil {
		t.Fatal("oversized WebP accepted")
	}
	if _, _, err := backgroundDimensions([]byte("not an image"), "png"); err == nil {
		t.Fatal("malformed PNG accepted")
	}
}

func TestJPEGOrientationDimensions(t *testing.T) {
	data := graphicFixture(t, 400, 800, "jpg")
	// EXIF little endian TIFF, orientation 6 (90 degrees clockwise).
	exif := []byte("Exif\x00\x00II\x2a\x00\x08\x00\x00\x00\x01\x00\x12\x01\x03\x00\x01\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00")
	segment := append([]byte{0xff, 0xe1, byte((len(exif) + 2) >> 8), byte(len(exif) + 2)}, exif...)
	oriented := append(append(append([]byte{}, data[:2]...), segment...), data[2:]...)
	w, h, err := backgroundDimensions(oriented, "jpg")
	if err != nil || w != 800 || h != 400 {
		t.Fatalf("EXIF dimensions: %d %d %v", w, h, err)
	}
}
