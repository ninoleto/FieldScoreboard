# Native Windows build. Run the Linux race check separately (scripts/build.sh).
$ErrorActionPreference = 'Stop'
Push-Location (Join-Path $PSScriptRoot '..')
$previousGOOS = $env:GOOS
$previousGOARCH = $env:GOARCH
$previousCGO = $env:CGO_ENABLED
function Invoke-Go {
    & go @args
    if ($LASTEXITCODE -ne 0) { throw "Go failed: $args" }
}
try {
    $env:GOOS = 'windows'
    $env:GOARCH = 'amd64'
    $env:CGO_ENABLED = '0'
    Invoke-Go test ./...
    Invoke-Go vet ./...
    Get-ChildItem internal/scoreboard/web/*.js | ForEach-Object {
        & node --check $_.FullName
        if ($LASTEXITCODE -ne 0) { throw "JS syntax failed: $_" }
    }
    New-Item -ItemType Directory bin -Force | Out-Null
    Invoke-Go build -trimpath '-ldflags=-s -w -H=windowsgui' -o bin/fieldscoreboard-windows.exe ./cmd/fieldscoreboard
    Invoke-Go build -trimpath '-ldflags=-s -w' -o bin/fieldscoreboard-windows-console.exe ./cmd/fieldscoreboard
    $env:GOOS = 'linux'
    Invoke-Go build -trimpath '-ldflags=-s -w' -o bin/fieldscoreboard-linux ./cmd/fieldscoreboard
    Write-Output 'Built Windows GUI, Windows console and Linux amd64 in bin/.'
} finally {
    $env:GOOS = $previousGOOS
    $env:GOARCH = $previousGOARCH
    $env:CGO_ENABLED = $previousCGO
    Pop-Location
}
