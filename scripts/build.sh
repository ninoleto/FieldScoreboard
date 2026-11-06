#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p bin
printf 'Field Scoreboard: Go tests and vet...\n'
go test ./...
go vet ./...
if [[ $(go env GOOS) == linux ]]; then
  go test -race ./...
fi
if command -v node >/dev/null 2>&1; then
  for js in internal/scoreboard/web/*.js; do node --check "$js"; done
fi
printf 'Compiling Windows and Linux x64 (no runtime dependencies)...\n'
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags='-s -w -H=windowsgui' -o bin/fieldscoreboard-windows.exe ./cmd/fieldscoreboard
CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build -trimpath -ldflags='-s -w' -o bin/fieldscoreboard-windows-console.exe ./cmd/fieldscoreboard
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -trimpath -ldflags='-s -w' -o bin/fieldscoreboard-linux ./cmd/fieldscoreboard
printf 'Built binaries in bin/.\n'
