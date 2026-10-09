-- TinyWMS seed data loaded from the sample inventory JSON

INSERT INTO products (sku, description, unit) VALUES
  ('SKU-1001', 'Blue widget', 'each'),
  ('SKU-1002', 'Red widget', 'each'),
  ('SKU-1003', 'Packing tape', 'roll');

INSERT INTO inventory_locations (sku, bin, quantity) VALUES
  ('SKU-1001', 'A1-01', 24),
  ('SKU-1002', 'A1-02', 8),
  ('SKU-1003', 'B2-04', 13);
