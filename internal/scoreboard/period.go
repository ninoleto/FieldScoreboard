package scoreboard

import (
	"errors"
	"regexp"
	"strconv"
	"strings"
)

func validPeriodFormat(format string) bool {
	return format == "number" || format == "ordinal" || format == "quarter"
}

func ordinalSuffix(n int) string {
	if n%100 >= 11 && n%100 <= 13 {
		return "th"
	}
	switch n % 10 {
	case 1:
		return "st"
	case 2:
		return "nd"
	case 3:
		return "rd"
	default:
		return "th"
	}
}

// Recognition and presentation are independent; the stored period is numeric.
func periodDisplay(n int, format string) string {
	value := strconv.Itoa(n)
	switch format {
	case "ordinal":
		return value + ordinalSuffix(n)
	case "quarter":
		return "Q" + value
	default:
		return value
	}
}

var periodPattern = regexp.MustCompile(`^(q)?([0-9]{1,2})(st|nd|rd|th)?$`)

func parseOCRPeriod(raw string) (int, error) {
	parts := periodPattern.FindStringSubmatch(strings.ToLower(strings.TrimSpace(raw)))
	if parts != nil {
		n, _ := strconv.Atoi(parts[2])
		if n >= 1 && n <= 20 && !(parts[1] != "" && parts[3] != "") && (parts[3] == "" || parts[3] == ordinalSuffix(n)) {
			return n, nil
		}
	}
	return 0, errors.New("expected period 1–20 as a number (3), valid ordinal (3rd), or Q-prefixed value (Q3)")
}
