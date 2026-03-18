-- Migration 002: Performance indexes
CREATE INDEX IF NOT EXISTS idx_inventory_product  ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_store    ON inventory(store_id);
CREATE INDEX IF NOT EXISTS idx_inventory_qty      ON inventory(quantity);
CREATE INDEX IF NOT EXISTS idx_shipments_status   ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_product  ON shipments(product_id);
CREATE INDEX IF NOT EXISTS idx_shipments_store    ON shipments(store_id);
CREATE INDEX IF NOT EXISTS idx_shipments_created  ON shipments(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_products_category  ON products(category);
CREATE INDEX IF NOT EXISTS idx_stores_region      ON stores(region);
