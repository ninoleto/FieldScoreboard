package scoreboard

import (
	"bytes"
	"encoding/binary"
	"errors"
	"image"
	_ "image/jpeg"
	_ "image/png"
	"math"
)

// Missing transforms deliberately retain the pre-test.6 stretched appearance.
// Coordinates are logical canvas pixels, never browser/display pixels.
type BackgroundTransform struct {
	Mode           string  `json:"mode"`
	Width          float64 `json:"width"`
	Height         float64 `json:"height"`
	X              float64 `json:"x"`
	Y              float64 `json:"y"`
	OriginalWidth  int     `json:"original_width"`
	OriginalHeight int     `json:"original_height"`
	LockAspect     bool    `json:"lock_aspect"`
}

// Accommodate even a 1x8192 image covering the canvas without truncating its ratio.
const MaxBackgroundExtent = CanvasW * 8192

func fitBackground(w, h int) *BackgroundTransform {
	scale := math.Min(float64(CanvasW)/float64(w), float64(CanvasH)/float64(h))
	width, height := float64(w)*scale, float64(h)*scale
	return &BackgroundTransform{Mode: "fit", Width: width, Height: height,
		X: (CanvasW - width) / 2, Y: (CanvasH - height) / 2,
		OriginalWidth: w, OriginalHeight: h, LockAspect: true}
}

func validateBackgroundTransform(t *BackgroundTransform) error {
	if t == nil {
		return nil
	}
	switch t.Mode {
	case "fit", "fill", "original", "stretch", "custom":
	default:
		return errors.New("invalid background sizing mode")
	}
	if t.OriginalWidth < 1 || t.OriginalWidth > 8192 || t.OriginalHeight < 1 || t.OriginalHeight > 8192 {
		return errors.New("original background dimensions must be 1–8192 pixels")
	}
	for _, v := range []float64{t.Width, t.Height, t.X, t.Y} {
		if math.IsNaN(v) || math.IsInf(v, 0) || math.Abs(v) > MaxBackgroundExtent {
			return errors.New("background transform is outside the supported range")
		}
	}
	if t.Width < .01 || t.Height < .01 {
		return errors.New("background dimensions must be at least 0.01 pixels")
	}
	return nil
}

// Read only headers, without decompressing or rewriting the original artwork.
func backgroundDimensions(data []byte, ext string) (int, int, error) {
	var w, h int
	var err error
	if ext == "webp" {
		w, h, err = webpDimensions(data)
	} else {
		var info image.Config
		info, _, err = image.DecodeConfig(bytes.NewReader(data))
		w, h = info.Width, info.Height
		if ext == "jpg" && jpegSwapsAxes(data) {
			w, h = h, w
		}
	}
	if err != nil || w < 1 || h < 1 || w > 8192 || h > 8192 {
		return 0, 0, errors.New("invalid image or dimensions exceed 8192 pixels")
	}
	return w, h, nil
}

// WebP RIFF headers: VP8X canvas, VP8 key-frame and VP8L lossless dimensions.
// https://developers.google.com/speed/webp/docs/riff_container
func webpDimensions(data []byte) (int, int, error) {
	bad := errors.New("invalid WebP dimensions")
	if len(data) < 20 || string(data[:4]) != "RIFF" || string(data[8:12]) != "WEBP" {
		return 0, 0, bad
	}
	end := uint64(binary.LittleEndian.Uint32(data[4:8])) + 8
	if end > uint64(len(data)) || end < 20 {
		return 0, 0, bad
	}
	var w, h int
	swap := false
	for offset := uint64(12); offset+8 <= end; {
		size := uint64(binary.LittleEndian.Uint32(data[offset+4 : offset+8]))
		start := offset + 8
		if size > end-start || start+size+(size&1) > end {
			return 0, 0, bad
		}
		chunk := data[start : start+size]
		switch string(data[offset : offset+4]) {
		case "VP8X":
			if len(chunk) < 10 {
				return 0, 0, bad
			}
			w = 1 + int(chunk[4]) + int(chunk[5])<<8 + int(chunk[6])<<16
			h = 1 + int(chunk[7]) + int(chunk[8])<<8 + int(chunk[9])<<16
		case "VP8 ":
			if w == 0 {
				if len(chunk) < 10 || !bytes.Equal(chunk[3:6], []byte{0x9d, 0x01, 0x2a}) {
					return 0, 0, bad
				}
				w, h = int(binary.LittleEndian.Uint16(chunk[6:8])&0x3fff), int(binary.LittleEndian.Uint16(chunk[8:10])&0x3fff)
			}
		case "VP8L":
			if w == 0 {
				if len(chunk) < 5 || chunk[0] != 0x2f {
					return 0, 0, bad
				}
				bits := binary.LittleEndian.Uint32(chunk[1:5])
				w, h = int(bits&0x3fff)+1, int((bits>>14)&0x3fff)+1
			}
		case "EXIF":
			swap = exifSwapsAxes(chunk)
		}
		offset = start + size + (size & 1)
	}
	if swap {
		w, h = h, w
	}
	if w == 0 || h == 0 {
		return 0, 0, bad
	}
	return w, h, nil
}

func jpegSwapsAxes(data []byte) bool {
	for pos := 2; pos+4 <= len(data) && data[pos] == 0xff; {
		marker := data[pos+1]
		if marker == 0xda || marker == 0xd9 {
			break
		}
		size := int(binary.BigEndian.Uint16(data[pos+2 : pos+4]))
		if size < 2 || pos+2+size > len(data) {
			break
		}
		if marker == 0xe1 && bytes.HasPrefix(data[pos+4:pos+2+size], []byte("Exif\x00\x00")) {
			return exifSwapsAxes(data[pos+4 : pos+2+size])
		}
		pos += 2 + size
	}
	return false
}

func exifSwapsAxes(data []byte) bool {
	data = bytes.TrimPrefix(data, []byte("Exif\x00\x00"))
	if len(data) < 8 {
		return false
	}
	var order binary.ByteOrder
	switch string(data[:2]) {
	case "II":
		order = binary.LittleEndian
	case "MM":
		order = binary.BigEndian
	default:
		return false
	}
	if order.Uint16(data[2:4]) != 42 {
		return false
	}
	offset := uint64(order.Uint32(data[4:8]))
	if offset+2 > uint64(len(data)) {
		return false
	}
	count := uint64(order.Uint16(data[offset : offset+2]))
	for pos, i := offset+2, uint64(0); i < count && pos+12 <= uint64(len(data)); pos, i = pos+12, i+1 {
		entry := data[pos : pos+12]
		if order.Uint16(entry[:2]) == 0x112 && order.Uint16(entry[2:4]) == 3 && order.Uint32(entry[4:8]) == 1 {
			orientation := order.Uint16(entry[8:10])
			return orientation >= 5 && orientation <= 8
		}
	}
	return false
}
