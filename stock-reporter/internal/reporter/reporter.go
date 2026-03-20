// reporter — core business logic.
//
// Architecture:
//   Reporter
//     ├── HTTP client → FastAPI GET /inventory?low_stock=true
//     ├── Kafka Producer → publishes StockEvent per low-stock item
//     └── N goroutines, one per store (N = cfg.StoreCount)
//
// Each goroutine runs an independent poll loop:
//   sleep(PollInterval) → fetch inventory → evaluate → publish events
//
// Goroutines communicate only via the shared done channel.
// No mutexes needed — each goroutine owns its own store slice.

package reporter

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/config"
	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/kafka"
	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/models"
)

type Reporter struct {
	cfg      *config.Config
	producer *kafka.Producer
	client   *http.Client
	done     chan struct{}
	wg       sync.WaitGroup
}

func New(cfg *config.Config) (*Reporter, error) {
	producer, err := kafka.NewProducer(cfg.KafkaBrokers, cfg.KafkaTopic)
	if err != nil {
		// Kafka unavailable — log warning but do not crash
		// Service will retry on next poll cycle
		log.Printf("[reporter] WARNING: Kafka unavailable: %v", err)
		log.Printf("[reporter] Starting in degraded mode — events will be logged only")
		producer = nil
	}

	return &Reporter{
		cfg:      cfg,
		producer: producer,
		client:   &http.Client{Timeout: 10 * time.Second},
		done:     make(chan struct{}),
	}, nil
}

// Start launches one goroutine per store.
// Each goroutine handles its own store slice of inventory.
func (r *Reporter) Start() {
	for storeID := 1; storeID <= r.cfg.StoreCount; storeID++ {
		r.wg.Add(1)
		go r.storeWorker(storeID)
	}
	log.Printf("[reporter] %d store workers started", r.cfg.StoreCount)
}

// storeWorker polls inventory for a single store on a fixed interval.
// This is the goroutine that costs ~2KB — trivial to run 10,000 of these.
func (r *Reporter) storeWorker(storeID int) {
	defer r.wg.Done()
	ticker := time.NewTicker(time.Duration(r.cfg.PollIntervalSec) * time.Second)
	defer ticker.Stop()

	log.Printf("[worker-%d] started", storeID)

	// Run once immediately, then on ticker
	r.checkStore(storeID)

	for {
		select {
		case <-ticker.C:
			r.checkStore(storeID)
		case <-r.done:
			log.Printf("[worker-%d] stopped", storeID)
			return
		}
	}
}

func (r *Reporter) checkStore(storeID int) {
	items, err := r.fetchLowStock(storeID)
	if err != nil {
		log.Printf("[worker-%d] fetch error: %v", storeID, err)
		return
	}

	for _, item := range items {
		event := r.buildEvent(item)
		if r.producer != nil {
			if err := r.producer.Publish(event); err != nil {
				log.Printf("[worker-%d] kafka publish error: %v", storeID, err)
			}
		} else {
			// Degraded mode — log the event instead
			log.Printf("[worker-%d] LOW_STOCK_EVENT product=%s store=%s qty=%d reorder=%d",
				storeID, item.ProductName, item.StoreName, item.Quantity, item.ReorderPoint)
		}
	}
}

func (r *Reporter) fetchLowStock(storeID int) ([]models.InventoryRecord, error) {
	url := fmt.Sprintf("%s/inventory?store_id=%d&low_stock=true&limit=100",
		r.cfg.APIBaseURL, storeID)

	req, _ := http.NewRequest("GET", url, nil)
	if r.cfg.APIToken != "" {
		req.Header.Set("Authorization", "Bearer "+r.cfg.APIToken)
	}

	resp, err := r.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("http request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API returned %d: %s", resp.StatusCode, string(body))
	}

	var records []models.InventoryRecord
	if err := json.NewDecoder(resp.Body).Decode(&records); err != nil {
		return nil, fmt.Errorf("decode error: %w", err)
	}
	return records, nil
}

func (r *Reporter) buildEvent(item models.InventoryRecord) models.StockEvent {
	severity := "warning"
	eventType := "low_stock"
	if item.Quantity == 0 {
		severity  = "critical"
		eventType = "critical"
	} else if item.Quantity <= item.ReorderPoint/2 {
		severity = "critical"
	}

	return models.StockEvent{
		EventType:    eventType,
		ProductID:    item.ProductID,
		StoreID:      item.StoreID,
		ProductName:  item.ProductName,
		StoreName:    item.StoreName,
		Quantity:     item.Quantity,
		ReorderPoint: item.ReorderPoint,
		Severity:     severity,
		Timestamp:    time.Now().UTC(),
	}
}

func (r *Reporter) Close() {
	close(r.done)
	r.wg.Wait()
	if r.producer != nil {
		r.producer.Close()
	}
	log.Println("[reporter] closed")
}
