package main

import (
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"time"
)

func mustParseURLFromEnv(envKey string) *url.URL {
	raw := os.Getenv(envKey)
	if raw == "" {
		log.Fatalf("CRITICAL ERROR: %s is not set in the environment. Service cannot start.", envKey)
	}
	parsed, err := url.Parse(raw)
	if err != nil || parsed.Scheme == "" || parsed.Host == "" {
		log.Fatalf("CRITICAL ERROR: %s must be a valid absolute URL. Received: %q", envKey, raw)
	}
	return parsed
}

func stripUpstreamCORSHeaders(resp *http.Response) error {
	resp.Header.Del("Access-Control-Allow-Origin")
	resp.Header.Del("Access-Control-Allow-Methods")
	resp.Header.Del("Access-Control-Allow-Headers")
	resp.Header.Del("Access-Control-Allow-Credentials")
	resp.Header.Del("Access-Control-Expose-Headers")
	resp.Header.Del("Access-Control-Max-Age")
	return nil
}

func newGatewayHandler(validApiKey string, ordersURL *url.URL, analyticsURL *url.URL) http.Handler {
	ordersProxy := httputil.NewSingleHostReverseProxy(ordersURL)
	analyticsProxy := httputil.NewSingleHostReverseProxy(analyticsURL)
	ordersProxy.ModifyResponse = stripUpstreamCORSHeaders
	analyticsProxy.ModifyResponse = stripUpstreamCORSHeaders
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()

		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, X-API-Key")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		// Validate API Key
		if r.Header.Get("X-API-Key") != validApiKey {
			log.Printf("UNAUTHORIZED: Blocked request from %s", r.RemoteAddr)
			http.Error(w, "Unauthorized", http.StatusUnauthorized)
			return
		}

		if strings.HasPrefix(r.URL.Path, "/orders") {
			ordersProxy.ServeHTTP(w, r)
		} else if strings.HasPrefix(r.URL.Path, "/analytics") {
			analyticsProxy.ServeHTTP(w, r)
		} else {
			http.Error(w, "Route not found", http.StatusNotFound)
			return
		}

		log.Printf("SUCCESS | Method: %s | Path: %s | Latency: %v", r.Method, r.URL.Path, time.Since(start))
	})
	return mux
}

func main() {
	ordersURL := mustParseURLFromEnv("ORDERS_UPSTREAM_URL")
	analyticsURL := mustParseURLFromEnv("ANALYTICS_UPSTREAM_URL")

	validApiKey := os.Getenv("ORDERS_API_KEY")
	if validApiKey == "" {
		log.Fatal("CRITICAL ERROR: ORDERS_API_KEY is not set in the environment. Service cannot start.")
	}

	handler := newGatewayHandler(validApiKey, ordersURL, analyticsURL)

	log.Printf("Gateway server listening on http://localhost:8080")
	if err := http.ListenAndServe(":8080", handler); err != nil {
		log.Fatal(err)
	}
}
