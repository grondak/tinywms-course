-- TinyWMS RDS bootstrap SQL
-- Run this against the RDS database after the instance is available.
-- The schema is the same one used for the self-managed Linux database lesson.

CREATE TABLE products (
    sku VARCHAR(32) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    unit VARCHAR(32) NOT NULL
);

CREATE TABLE inventory_locations (
    sku VARCHAR(32) NOT NULL,
    bin VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    PRIMARY KEY (sku, bin),
    FOREIGN KEY (sku) REFERENCES products(sku)
);

INSERT INTO products (sku, description, unit) VALUES
  ('SKU-1001', 'Blue widget', 'each'),
  ('SKU-1002', 'Red widget', 'each'),
  ('SKU-1003', 'Packing tape', 'roll');

INSERT INTO inventory_locations (sku, bin, quantity) VALUES
  ('SKU-1001', 'A1-01', 24),
  ('SKU-1002', 'A1-02', 8),
  ('SKU-1003', 'B2-04', 13);
