package main

import (
	"net/http/httptest"
	"strings"
	"testing"
)

func TestNativeRoutes(t *testing.T) {
	for _, tc := range []struct {
		path   string
		want   int
		needle string
	}{
		{"/", 302, ""}, {"/healthz", 200, "LaNonApp"}, {"/app/", 200, "LaNonApp"}, {"/app/vault.js", 200, "PBKDF2"}, {"/site/", 200, "LaNonApp"}, {"/api/x", 404, ""},
	} {
		r := httptest.NewRequest("GET", "http://127.0.0.1:18765"+tc.path, nil)
		w := httptest.NewRecorder()
		handler().ServeHTTP(w, r)
		if w.Code != tc.want {
			t.Fatalf("%s: %d != %d", tc.path, w.Code, tc.want)
		}
		if tc.needle != "" && !strings.Contains(w.Body.String(), tc.needle) {
			t.Fatalf("%s missing %q", tc.path, tc.needle)
		}
	}
}
func TestNativeSafety(t *testing.T) {
	for _, tc := range []struct {
		method string
		host   string
		want   int
	}{{"POST", "127.0.0.1:18765", 405}, {"GET", "malicious.example", 403}} {
		r := httptest.NewRequest(tc.method, "http://127.0.0.1:18765/app/index.html", nil)
		r.Host = tc.host
		w := httptest.NewRecorder()
		handler().ServeHTTP(w, r)
		if w.Code != tc.want {
			t.Fatalf("%s %s: %d != %d", tc.method, tc.host, w.Code, tc.want)
		}
	}
}
func TestVersionHeader(t *testing.T) {
	r := httptest.NewRequest("GET", "http://127.0.0.1:18765/healthz", nil)
	w := httptest.NewRecorder()
	handler().ServeHTTP(w, r)
	if w.Header().Get("X-LaNonApp-Version") != version {
		t.Fatalf("version header missing")
	}
}
