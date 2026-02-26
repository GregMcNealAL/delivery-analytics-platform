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

func main() {
	ordersURL, _ := url.Parse("http://localhost:8000")
	analyticsURL, _ := url.Parse("http://localhost:8001")

	ordersProxy := httputil.NewSingleHostReverseProxy(ordersURL)
	analyticsProxy := httputil.NewSingleHostReverseProxy(analyticsURL)

	validApiKey := os.Getenv("ORDERS_API_KEY")

	if validApiKey == "" {
		log.Fatal("CRITICAL ERROR: ORDERS_API_KEY is not set in the environment. Service cannot start.")
	}

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
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

	log.Printf("Gateway server listening on http://localhost:8080")
	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatal(err)
	}
}
