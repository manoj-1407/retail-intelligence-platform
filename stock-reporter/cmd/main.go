// stock-reporter — Go microservice
//
// WHY GO FOR THIS SERVICE?
//
// This service runs one goroutine per store (10 stores = 10 goroutines).
// Each goroutine polls inventory levels and publishes Kafka events when
// stock drops below the reorder point.
//
// Go goroutines cost ~2KB each. Java threads cost ~1MB each.
// 10,000 store reporters in Go  = ~20MB RAM
// 10,000 store reporters in Java = ~10GB RAM
//
// For a service whose only job is "check stock, emit event", Go is the
// correct tool. Python would work but has the GIL — true parallelism
// requires multiprocessing. Go goroutines are genuinely concurrent.

package main

import (
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/joho/godotenv"
	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/config"
	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/reporter"
)

func main() {
	// Load .env if present (ignored in Docker — env vars injected directly)
	_ = godotenv.Load()

	cfg := config.Load()

	log.Printf("[stock-reporter] starting | brokers=%s topic=%s stores=%d poll=%ds",
		cfg.KafkaBrokers, cfg.KafkaTopic, cfg.StoreCount, cfg.PollIntervalSec)

	r, err := reporter.New(cfg)
	if err != nil {
		log.Fatalf("[stock-reporter] failed to create reporter: %v", err)
	}
	defer r.Close()

	// Start one goroutine per store
	r.Start()

	// Block until SIGINT or SIGTERM
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Println("[stock-reporter] shutting down gracefully")
}
