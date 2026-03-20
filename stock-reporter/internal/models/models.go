// models — shared data structures.
// Kept in one file because the service is small and cohesion > separation here.

package models

import "time"

// StockEvent is published to Kafka when inventory drops below reorder point.
// JSON-serialised directly — no protobuf needed at this scale.
type StockEvent struct {
	EventType    string    `json:"event_type"`    // "low_stock" | "restock" | "critical"
	ProductID    int       `json:"product_id"`
	StoreID      int       `json:"store_id"`
	ProductName  string    `json:"product_name"`
	StoreName    string    `json:"store_name"`
	Quantity     int       `json:"quantity"`
	ReorderPoint int       `json:"reorder_point"`
	Severity     string    `json:"severity"`      // "warning" | "critical"
	Timestamp    time.Time `json:"timestamp"`
}

// InventoryRecord mirrors the JSON returned by GET /inventory
type InventoryRecord struct {
	ID           int    `json:"id"`
	ProductID    int    `json:"product_id"`
	StoreID      int    `json:"store_id"`
	Quantity     int    `json:"quantity"`
	ReorderPoint int    `json:"reorder_point"`
	ProductName  string `json:"product_name"`
	StoreName    string `json:"store_name"`
}
