-- Seed data for development and testing
INSERT INTO products (sku, name, category, unit_cost, unit_price) VALUES
  ('ELEC-001', 'Samsung 65-inch QLED TV',     'Electronics',  399.99, 799.99),
  ('ELEC-002', 'Apple AirPods Pro',            'Electronics',   89.00, 249.00),
  ('ELEC-003', 'Sony PlayStation 5',           'Electronics',  399.00, 499.99),
  ('GROC-001', 'Organic Whole Milk 1 Gallon',  'Grocery',        2.10,   4.99),
  ('GROC-002', 'Lays Classic Chips 10oz',      'Grocery',        1.20,   3.49),
  ('CLTH-001', 'Levis 501 Original Jeans',     'Clothing',      35.00,  79.99),
  ('CLTH-002', 'Nike Air Max 270',             'Clothing',      75.00, 159.99),
  ('HOME-001', 'Instant Pot Duo 7-in-1',       'Home',          45.00,  99.99),
  ('HOME-002', 'Dyson V15 Vacuum',             'Home',         220.00, 699.99),
  ('TOYS-001', 'LEGO Technic Bugatti',         'Toys',         185.00, 449.99)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO stores (store_code, name, region, capacity) VALUES
  ('WMT-TX-001', 'Walmart Supercenter Austin',     'South',     50000),
  ('WMT-TX-002', 'Walmart Supercenter Houston',    'South',     55000),
  ('WMT-CA-001', 'Walmart Supercenter Los Angeles','West',      48000),
  ('WMT-CA-002', 'Walmart Supercenter San Diego',  'West',      42000),
  ('WMT-NY-001', 'Walmart Supercenter New York',   'Northeast', 38000),
  ('WMT-FL-001', 'Walmart Supercenter Miami',      'Southeast', 51000),
  ('WMT-IL-001', 'Walmart Supercenter Chicago',    'Midwest',   46000),
  ('WMT-WA-001', 'Walmart Supercenter Seattle',    'Northwest', 44000),
  ('WMT-GA-001', 'Walmart Supercenter Atlanta',    'Southeast', 49000),
  ('WMT-AZ-001', 'Walmart Supercenter Phoenix',    'West',      52000)
ON CONFLICT (store_code) DO NOTHING;

INSERT INTO inventory (product_id, store_id, quantity, reorder_point)
SELECT
    p.id,
    s.id,
    (random() * 200 + 10)::INTEGER,
    CASE
        WHEN p.category = 'Electronics' THEN 5
        WHEN p.category = 'Grocery'     THEN 50
        ELSE 15
    END
FROM products p CROSS JOIN stores s
ON CONFLICT (product_id, store_id) DO NOTHING;

INSERT INTO shipments (product_id, store_id, quantity, status, shipped_at, delivered_at)
SELECT
    p.id,
    s.id,
    (random() * 50 + 5)::INTEGER,
    CASE (random() * 3)::INTEGER
        WHEN 0 THEN 'delivered'
        WHEN 1 THEN 'in_transit'
        ELSE 'pending'
    END,
    NOW() - (random() * INTERVAL '10 days'),
    CASE WHEN (random() * 3)::INTEGER = 0
        THEN NOW() - (random() * INTERVAL '2 days')
        ELSE NULL
    END
FROM products p CROSS JOIN stores s
LIMIT 50;
