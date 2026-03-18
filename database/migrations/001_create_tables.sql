-- Migration 001: Core schema
-- Products table
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    sku         VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    unit_cost   NUMERIC(10,2) NOT NULL CHECK (unit_cost > 0),
    unit_price  NUMERIC(10,2) NOT NULL CHECK (unit_price > unit_cost),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Stores table
CREATE TABLE IF NOT EXISTS stores (
    id          SERIAL PRIMARY KEY,
    store_code  VARCHAR(20) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    region      VARCHAR(100) NOT NULL,
    capacity    INTEGER NOT NULL CHECK (capacity > 0),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Inventory table (product x store stock levels)
CREATE TABLE IF NOT EXISTS inventory (
    id            SERIAL PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id      INTEGER NOT NULL REFERENCES stores(id) ON DELETE CASCADE,
    quantity      INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_point INTEGER NOT NULL DEFAULT 10,
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(product_id, store_id)
);

-- Shipments table
CREATE TABLE IF NOT EXISTS shipments (
    id            SERIAL PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES products(id),
    store_id      INTEGER NOT NULL REFERENCES stores(id),
    quantity      INTEGER NOT NULL CHECK (quantity > 0),
    status        VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','in_transit','delivered','cancelled')),
    shipped_at    TIMESTAMPTZ,
    delivered_at  TIMESTAMPTZ,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);
