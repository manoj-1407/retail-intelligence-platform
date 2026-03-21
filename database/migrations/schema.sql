-- ============================================================
-- Retail Intelligence Platform — Database Schema
-- Generated from Alembic migration 0001_initial_schema
-- ============================================================

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Stores ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS stores (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL UNIQUE,
    location    VARCHAR(255),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name);

-- ── Products ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    price       NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    cost        NUMERIC(10, 2) NOT NULL CHECK (cost >= 0),
    sku         VARCHAR(100) UNIQUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_sku      ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_name     ON products(name);

-- ── Inventory ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventory (
    id            SERIAL PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id      INTEGER NOT NULL REFERENCES stores(id)   ON DELETE CASCADE,
    quantity      INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_point INTEGER NOT NULL DEFAULT 10,
    updated_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (product_id, store_id)
);

CREATE INDEX IF NOT EXISTS idx_inventory_product  ON inventory(product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_store    ON inventory(store_id);
CREATE INDEX IF NOT EXISTS idx_inventory_qty      ON inventory(quantity);
CREATE INDEX IF NOT EXISTS idx_inventory_low_stock
    ON inventory(quantity) WHERE quantity <= reorder_point;

-- ── Shipments ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shipments (
    id          SERIAL PRIMARY KEY,
    product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    store_id    INTEGER NOT NULL REFERENCES stores(id)   ON DELETE CASCADE,
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    status      VARCHAR(50) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'in_transit', 'delivered', 'cancelled')),
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_shipments_status     ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_product    ON shipments(product_id);
CREATE INDEX IF NOT EXISTS idx_shipments_store      ON shipments(store_id);
CREATE INDEX IF NOT EXISTS idx_shipments_created_at ON shipments(created_at DESC);

-- ── Seed data (10 stores, 10 products, 100 inventory rows) ──────────
INSERT INTO stores (name, location) VALUES
    ('Store Alpha',   'Mumbai'),
    ('Store Beta',    'Delhi'),
    ('Store Gamma',   'Bangalore'),
    ('Store Delta',   'Chennai'),
    ('Store Epsilon', 'Hyderabad'),
    ('Store Zeta',    'Kolkata'),
    ('Store Eta',     'Pune'),
    ('Store Theta',   'Ahmedabad'),
    ('Store Iota',    'Jaipur'),
    ('Store Kappa',   'Surat')
ON CONFLICT (name) DO NOTHING;

INSERT INTO products (name, category, price, cost, sku) VALUES
    ('Laptop Pro 15',      'Electronics',  89999.00, 65000.00, 'ELEC-001'),
    ('Wireless Mouse',     'Electronics',   1299.00,   600.00, 'ELEC-002'),
    ('USB-C Hub',          'Electronics',   2499.00,  1100.00, 'ELEC-003'),
    ('Office Chair',       'Furniture',    12999.00,  7000.00, 'FURN-001'),
    ('Standing Desk',      'Furniture',    24999.00, 14000.00, 'FURN-002'),
    ('Notebook A5',        'Stationery',     199.00,    60.00, 'STAT-001'),
    ('Ballpoint Pens 10x', 'Stationery',     149.00,    40.00, 'STAT-002'),
    ('Water Bottle 1L',    'Kitchen',        599.00,   180.00, 'KITCH-001'),
    ('Coffee Mug',         'Kitchen',        399.00,   100.00, 'KITCH-002'),
    ('Desk Lamp LED',      'Electronics',   1999.00,   800.00, 'ELEC-004')
ON CONFLICT (sku) DO NOTHING;

-- 100 inventory rows (10 products x 10 stores)
INSERT INTO inventory (product_id, store_id, quantity, reorder_point)
SELECT
    p.id,
    s.id,
    -- Vary quantity: some low stock, some normal
    CASE WHEN (p.id + s.id) % 5 = 0 THEN 3
         WHEN (p.id + s.id) % 7 = 0 THEN 8
         ELSE 20 + (p.id * s.id % 80)
    END,
    10
FROM products p CROSS JOIN stores s
ON CONFLICT (product_id, store_id) DO NOTHING;

-- Sample shipments
INSERT INTO shipments (product_id, store_id, quantity, status) VALUES
    (1, 1, 5,  'delivered'),
    (2, 1, 20, 'in_transit'),
    (3, 2, 10, 'pending'),
    (4, 3, 3,  'delivered'),
    (5, 4, 2,  'cancelled'),
    (1, 5, 8,  'in_transit'),
    (6, 6, 50, 'delivered'),
    (7, 7, 30, 'pending'),
    (8, 8, 15, 'in_transit'),
    (9, 9, 12, 'delivered')
ON CONFLICT DO NOTHING;
