-- TinyWMS relational schema for the inventory lesson
-- Designed for PostgreSQL or MariaDB with ordinary SQL types.

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

CREATE INDEX idx_inventory_locations_bin ON inventory_locations(bin);
