//go:build !windows

package main

import (
	"context"
	"fmt"
)

func hasTray() bool { return false }
func runTray(ctx context.Context, url string, outputFolder func() string, quit func()) error {
	return fmt.Errorf("system tray is not implemented on this platform")
}
func showFatal(message string) {}
