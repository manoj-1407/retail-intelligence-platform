package reporter

import (
	"testing"
	"time"

	"github.com/manoj-1407/retail-intelligence-platform/stock-reporter/internal/models"
)

func TestBuildEvent_Warning(t *testing.T) {
	r := &Reporter{}
	item := models.InventoryRecord{
		ProductID: 1, StoreID: 2,
		ProductName: "Samsung TV", StoreName: "Austin",
		Quantity: 8, ReorderPoint: 10,
	}
	event := r.buildEvent(item)

	if event.Severity != "warning" {
		t.Errorf("expected warning, got %s", event.Severity)
	}
	if event.EventType != "low_stock" {
		t.Errorf("expected low_stock, got %s", event.EventType)
	}
	if event.ProductID != 1 {
		t.Errorf("expected product_id=1, got %d", event.ProductID)
	}
}

func TestBuildEvent_Critical_Zero(t *testing.T) {
	r := &Reporter{}
	item := models.InventoryRecord{
		Quantity: 0, ReorderPoint: 5,
		ProductName: "AirPods", StoreName: "Houston",
	}
	event := r.buildEvent(item)
	if event.Severity != "critical" {
		t.Errorf("expected critical for zero stock, got %s", event.Severity)
	}
	if event.EventType != "critical" {
		t.Errorf("expected critical event type, got %s", event.EventType)
	}
}

func TestBuildEvent_Critical_HalfReorder(t *testing.T) {
	r := &Reporter{}
	item := models.InventoryRecord{
		Quantity: 2, ReorderPoint: 10,
	}
	event := r.buildEvent(item)
	if event.Severity != "critical" {
		t.Errorf("expected critical when qty <= reorder/2, got %s", event.Severity)
	}
}

func TestBuildEvent_Timestamp(t *testing.T) {
	r := &Reporter{}
	before := time.Now().UTC()
	event := r.buildEvent(models.InventoryRecord{Quantity: 5, ReorderPoint: 10})
	after := time.Now().UTC()

	if event.Timestamp.Before(before) || event.Timestamp.After(after) {
		t.Error("timestamp should be set to current UTC time")
	}
}
