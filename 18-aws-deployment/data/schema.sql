-- TinyWMS relational schema for the inventory and orders lessons
-- Designed for PostgreSQL or MariaDB with ordinary SQL types.
-- In the concurrency lesson, oversell prevention comes from transaction logic
-- in application SQL, not from changing the logical table model.

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

CREATE TABLE orders (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_lines (
    order_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    sku VARCHAR(32) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (order_id, line_number),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (sku) REFERENCES products(sku)
);
