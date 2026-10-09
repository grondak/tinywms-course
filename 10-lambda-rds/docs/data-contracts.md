# TinyWMS data contracts

## Inventory JSON document
TinyWMS uses one top-level JSON object containing an `inventory` array.

### Fields
- `inventory` - array of product records
- `inventory[].sku` - stable product identifier used by CLI, HTTP, browser, Lambda, API Gateway, and relational mapping examples
- `inventory[].description` - human-readable product description
- `inventory[].bin` - warehouse bin or shelf location
- `inventory[].quantity` - on-hand count as a non-negative integer
- `inventory[].unit` - unit of measure such as `each`, `box`, or `case`

## Relational mapping
The relational lesson keeps the same inventory meaning but stores it in tables.

### Table: `products`
- `sku` - primary key, copied from `inventory[].sku`
- `description` - copied from `inventory[].description`
- `unit` - copied from `inventory[].unit`

### Table: `inventory_locations`
- `sku` - foreign key to `products.sku`
- `bin` - copied from `inventory[].bin`
- `quantity` - copied from `inventory[].quantity`

### RDS note
When the database is moved to Amazon RDS, the table structure and mapping do not change. Only the operational home of the same schema changes.

### Lambda-to-RDS note
When Lambda starts reading from RDS, it must convert database rows back into this exact JSON document shape. The browser and earlier HTTP lessons continue to rely on the same `inventory[]` fields.

### Optional order tables
Later lessons may add orders and order lines. This stage does not require them yet, but the schema is intentionally organized so that future order rows can reference `products` without changing the basic product contract.

## JSON-to-table mapping notes
- One JSON inventory item becomes one `products` row and one `inventory_locations` row.
- The JSON document itself remains the teaching contract for the application boundary.
- SQL is used for persistence in this stage; Lambda now reads SQL rows and emits the same JSON response body used in the earlier stages.

## Notes
- The model stays intentionally small so beginning students can understand it immediately.
- Later stages must preserve this JSON meaning unless a lesson explicitly says otherwise.
