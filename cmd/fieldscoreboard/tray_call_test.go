package main

import (
	"go/ast"
	"go/parser"
	"go/token"
	"path/filepath"
	"testing"
)

// TestCreateWindowExWABI statically checks a Win32 call that cannot be
// exercised by Linux CI. A previous release accidentally passed 11 args
// instead of 12, so Windows read hInstance as hMenu and rejected the window.
func TestCreateWindowExWABI(t *testing.T) {
	filename := filepath.Join("tray_windows.go")
	file, err := parser.ParseFile(token.NewFileSet(), filename, nil, 0)
	if err != nil {
		t.Fatal(err)
	}
	found := false
	ast.Inspect(file, func(node ast.Node) bool {
		call, ok := node.(*ast.CallExpr)
		if !ok {
			return true
		}
		sel, ok := call.Fun.(*ast.SelectorExpr)
		if !ok || sel.Sel.Name != "Call" {
			return true
		}
		ident, ok := sel.X.(*ast.Ident)
		if !ok || ident.Name != "createWindow" {
			return true
		}
		found = true
		if len(call.Args) != 12 {
			t.Errorf("CreateWindowExW requires 12 args, got %d", len(call.Args))
			return false
		}
		isZero := func(node ast.Expr) bool {
			v, ok := node.(*ast.BasicLit)
			return ok && v.Value == "0"
		}
		if !isZero(call.Args[9]) {
			t.Error("10th CreateWindowExW argument (hMenu) must be zero")
		}
		if instance, ok := call.Args[10].(*ast.Ident); !ok || instance.Name != "instance" {
			t.Error("11th CreateWindowExW argument must be hInstance")
		}
		if !isZero(call.Args[11]) {
			t.Error("12th CreateWindowExW argument (lpParam) must be zero")
		}
		return false
	})
	if !found {
		t.Error("CreateWindowExW call not found in tray_windows.go")
	}
}
