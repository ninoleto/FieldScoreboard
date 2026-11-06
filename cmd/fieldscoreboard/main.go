package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"runtime"
	"syscall"
	"time"

	"fieldscoreboard/internal/scoreboard"
)

func openBrowser(url string) {
	var c *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		c = exec.Command("rundll32.exe", "url.dll,FileProtocolHandler", url)
	case "linux":
		c = exec.Command("xdg-open", url)
	default:
		return
	}
	if err := c.Start(); err != nil {
		log.Printf("browser launch: %v", err)
	}
}
func openOutputFolder(path string) {
	if path == "" {
		return
	}
	var c *exec.Cmd
	if runtime.GOOS == "windows" {
		c = exec.Command("explorer.exe", path)
	} else {
		c = exec.Command("xdg-open", path)
	}
	if err := c.Start(); err != nil {
		log.Printf("open data folder: %v", err)
	}
}
func main() {
	log.SetFlags(log.Ldate | log.Ltime)
	fatal := func(err error) { showFatal(err.Error()); log.Fatal(err) }
	var configPath, override string
	var autoOpen, showToken bool
	flag.StringVar(&configPath, "config", "", "path to config.json (default user config folder)")
	flag.StringVar(&override, "listen", "", "override listen address for this run")
	flag.BoolVar(&autoOpen, "open", true, "open local web UI on launch")
	flag.BoolVar(&showToken, "show-token", false, "print local API token and exit")
	flag.Parse()
	if configPath == "" {
		p, err := scoreboard.ConfigPath()
		if err != nil {
			fatal(err)
		}
		configPath = p
	}
	p, err := filepath.Abs(configPath)
	if err != nil {
		fatal(err)
	}
	configPath = p
	cfg, err := scoreboard.LoadOrCreate(configPath)
	if err != nil {
		fatal(err)
	}
	if showToken {
		fmt.Println(cfg.Token)
		return
	}
	if runtime.GOOS == "windows" {
		file, err := os.OpenFile(filepath.Join(filepath.Dir(configPath), "fieldscoreboard.log"), os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
		if err == nil {
			defer file.Close()
			log.SetOutput(file)
		} else {
			log.SetOutput(io.Discard)
		}
	}
	listen := cfg.Listen
	if override != "" {
		c := cfg
		c.Listen = override
		if err := scoreboard.ValidateConfig(c); err != nil {
			fatal(err)
		}
		listen = override
	}
	app, err := scoreboard.NewApp(cfg, configPath)
	if err != nil {
		fatal(err)
	}
	// The --listen test override affects only this running instance.
	app.SetActiveListen(listen)
	srv, err := scoreboard.NewServer(app)
	if err != nil {
		fatal(err)
	}
	listener, err := net.Listen("tcp", listen)
	if err != nil {
		fatal(err)
	}
	server := scoreboard.HTTPServer(srv, listen)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	go srv.RunClockLoop(ctx)
	localURL := "http://127.0.0.1:" + scoreboard.ParsePort(listen) + "/"
	log.Printf("Field Scoreboard v%s | Web %s | Listen %s | Config %s", scoreboard.Version, localURL, listen, configPath)
	go func() {
		if err := server.Serve(listener); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Printf("HTTP error: %v", err)
		}
		stop()
	}()
	if autoOpen {
		go func() { time.Sleep(220 * time.Millisecond); openBrowser(localURL) }()
	}
	if hasTray() {
		if err := runTray(ctx, localURL, func() string { return filepath.Dir(configPath) }, stop); err != nil {
			log.Printf("tray error: %v", err)
			showFatal(fmt.Sprintf("Cannot start Field Scoreboard tray: %v", err))
		}
		stop()
	} else {
		<-ctx.Done()
	}
	c, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_ = server.Shutdown(c)
}
