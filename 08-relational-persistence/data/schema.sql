CREATE TABLE inventory (
  sku TEXT PRIMARY KEY,
  description TEXT NOT NULL,
  bin_location TEXT NOT NULL,
  quantity INTEGER NOT NULL CHECK (quantity >= 0),
  unit TEXT NOT NULL
);
