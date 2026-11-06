//go:build windows

package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"syscall"
	"unsafe"
)

// A tiny Win32 notification-area implementation with no external packages or
// cgo. Keeping this separate allows the Linux binary to remain headless.
const (
	wmClose         = 0x0010
	wmDestroy       = 0x0002
	wmUserTray      = 0x8001
	wmLButtonDblClk = 0x0203
	wmRButtonUp     = 0x0205
	nifMessage      = 1
	nifIcon         = 2
	nifTip          = 4
	nimAdd          = 0
	nimDelete       = 2
	mfSeparator     = 0x800
	mfString        = 0
	tpmRightButton  = 0x0002
	tpmReturnCmd    = 0x0100
	imageIcon       = 1
	lrLoadFromFile  = 0x10
	lrDefaultSize   = 0x40
)

type winClass struct {
	size        uint32
	style       uint32
	callback    uintptr
	classExtra  int32
	windowExtra int32
	instance    uintptr
	icon        uintptr
	cursor      uintptr
	background  uintptr
	menu        *uint16
	class       *uint16
	smallIcon   uintptr
}

type winPoint struct{ x, y int32 }
type winMsg struct {
	hwnd    uintptr
	message uint32
	wparam  uintptr
	lparam  uintptr
	at      uint32
	pt      winPoint
	private uint32
}
type notifyIcon struct {
	size        uint32
	hwnd        uintptr
	id          uint32
	flags       uint32
	callback    uint32
	icon        uintptr
	tip         [128]uint16
	state       uint32
	stateMask   uint32
	info        [256]uint16
	timeout     uint32
	infoTitle   [64]uint16
	infoFlags   uint32
	guid        [16]byte
	balloonIcon uintptr
}

var (
	user32           = syscall.NewLazyDLL("user32.dll")
	shell32Tray      = syscall.NewLazyDLL("shell32.dll")
	kernel32Tray     = syscall.NewLazyDLL("kernel32.dll")
	registerClass    = user32.NewProc("RegisterClassExW")
	createWindow     = user32.NewProc("CreateWindowExW")
	destroyWindow    = user32.NewProc("DestroyWindow")
	defWindowProc    = user32.NewProc("DefWindowProcW")
	getMessage       = user32.NewProc("GetMessageW")
	translateMessage = user32.NewProc("TranslateMessage")
	dispatchMessage  = user32.NewProc("DispatchMessageW")
	postQuit         = user32.NewProc("PostQuitMessage")
	postMessage      = user32.NewProc("PostMessageW")
	getCursor        = user32.NewProc("GetCursorPos")
	createPopupMenu  = user32.NewProc("CreatePopupMenu")
	appendMenu       = user32.NewProc("AppendMenuW")
	destroyMenu      = user32.NewProc("DestroyMenu")
	trackPopupMenu   = user32.NewProc("TrackPopupMenu")
	setForeground    = user32.NewProc("SetForegroundWindow")
	loadImage        = user32.NewProc("LoadImageW")
	loadIcon         = user32.NewProc("LoadIconW")
	destroyIcon      = user32.NewProc("DestroyIcon")
	shellNotify      = shell32Tray.NewProc("Shell_NotifyIconW")
	moduleHandle     = kernel32Tray.NewProc("GetModuleHandleW")
	messageBox       = user32.NewProc("MessageBoxW")
)
var trayOpen func()
var trayFolder func()
var trayQuit func()
var trayNotify notifyIcon

func winString(s string) *uint16 { p, _ := syscall.UTF16PtrFromString(s); return p }

func trayWindowProc(hwnd uintptr, msg uint32, wparam, lparam uintptr) uintptr {
	switch msg {
	case wmUserTray:
		switch uint32(lparam) {
		case wmLButtonDblClk:
			if trayOpen != nil {
				trayOpen()
			}
		case wmRButtonUp:
			menu, _, _ := createPopupMenu.Call()
			if menu != 0 {
				appendMenu.Call(menu, mfString, 101, uintptr(unsafe.Pointer(winString("Open Field Scoreboard"))))
				appendMenu.Call(menu, mfString, 102, uintptr(unsafe.Pointer(winString("Open data folder"))))
				appendMenu.Call(menu, mfSeparator, 0, 0)
				appendMenu.Call(menu, mfString, 103, uintptr(unsafe.Pointer(winString("Exit Field Scoreboard"))))
				var pt winPoint
				getCursor.Call(uintptr(unsafe.Pointer(&pt)))
				setForeground.Call(hwnd)
				id, _, _ := trackPopupMenu.Call(menu, tpmRightButton|tpmReturnCmd, uintptr(pt.x), uintptr(pt.y), 0, hwnd, 0)
				destroyMenu.Call(menu)
				switch id {
				case 101:
					if trayOpen != nil {
						trayOpen()
					}
				case 102:
					if trayFolder != nil {
						trayFolder()
					}
				case 103:
					if trayQuit != nil {
						trayQuit()
					}
				}
			}
		}
		return 0
	case wmClose:
		destroyWindow.Call(hwnd)
		return 0
	case wmDestroy:
		shellNotify.Call(nimDelete, uintptr(unsafe.Pointer(&trayNotify)))
		postQuit.Call(0)
		return 0
	}
	result, _, _ := defWindowProc.Call(hwnd, uintptr(msg), wparam, lparam)
	return result
}

func runTray(ctx context.Context, openURL string, outputFolder func() string, quit func()) error {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	trayOpen = func() { openBrowser(openURL) }
	trayFolder = func() { openOutputFolder(outputFolder()) }
	trayQuit = quit
	instance, _, _ := moduleHandle.Call(0)
	className := winString(fmt.Sprintf("FieldScoreboard_Tray_%d", os.Getpid()))
	callback := syscall.NewCallback(trayWindowProc)
	wc := winClass{size: uint32(unsafe.Sizeof(winClass{})), callback: callback, instance: instance, class: className}
	if n, _, err := registerClass.Call(uintptr(unsafe.Pointer(&wc))); n == 0 {
		return fmt.Errorf("register tray window: %w", err)
	}
	// CreateWindowExW takes twelve arguments. The ninth is hWndParent,
	// the tenth is hMenu, and the eleventh is hInstance. Never omit the
	// zero hMenu argument: Windows treats hInstance as a menu handle and
	// rejects the call with ERROR_INVALID_MENU_HANDLE (1401).
	hwnd, _, err := createWindow.Call(
		0,                                  // dwExStyle
		uintptr(unsafe.Pointer(className)), // lpClassName
		0,                                  // lpWindowName
		0,                                  // dwStyle
		0, 0, 0, 0,                         // x, y, width, height
		0,        // hWndParent
		0,        // hMenu (must not be omitted)
		instance, // hInstance
		0,        // lpParam
	)
	if hwnd == 0 {
		return fmt.Errorf("create tray window: %w", err)
	}
	icon := uintptr(0)
	if exe, err := os.Executable(); err == nil {
		path := winString(filepath.Join(filepath.Dir(exe), "fieldscoreboard.ico"))
		icon, _, _ = loadImage.Call(0, uintptr(unsafe.Pointer(path)), imageIcon, 0, 0, lrLoadFromFile|lrDefaultSize)
	}
	ownsIcon := icon != 0
	if icon == 0 {
		icon, _, _ = loadIcon.Call(0, 32512)
	} // IDI_APPLICATION fallback
	trayNotify = notifyIcon{size: uint32(unsafe.Sizeof(notifyIcon{})), hwnd: hwnd, id: 1, flags: nifMessage | nifIcon | nifTip, callback: wmUserTray, icon: icon}
	copy(trayNotify.tip[:], syscall.StringToUTF16("Field Scoreboard - double-click to open"))
	if n, _, err := shellNotify.Call(nimAdd, uintptr(unsafe.Pointer(&trayNotify))); n == 0 {
		destroyWindow.Call(hwnd)
		return fmt.Errorf("create notification icon: %w", err)
	}
	defer func() {
		if ownsIcon && icon != 0 {
			destroyIcon.Call(icon)
		}
	}()
	go func() { <-ctx.Done(); postMessage.Call(hwnd, wmClose, 0, 0) }()
	var msg winMsg
	for {
		n, _, err := getMessage.Call(uintptr(unsafe.Pointer(&msg)), 0, 0, 0)
		if n == 0 {
			return nil
		}
		if n == ^uintptr(0) {
			return fmt.Errorf("tray message loop: %w", err)
		}
		translateMessage.Call(uintptr(unsafe.Pointer(&msg)))
		dispatchMessage.Call(uintptr(unsafe.Pointer(&msg)))
	}
}

func showFatal(message string) {
	text := winString(message)
	caption := winString("Field Scoreboard error")
	messageBox.Call(0, uintptr(unsafe.Pointer(text)), uintptr(unsafe.Pointer(caption)), 0x10)
}

func hasTray() bool { return true }
