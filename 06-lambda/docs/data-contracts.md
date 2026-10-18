# TinyWMS Data Contracts

This document describes the TinyWMS inventory JSON contract.

## Inventory JSON

Inventory is stored as a JSON array of objects. Each object represents one stock item and is reused by the CLI, the Linux demo tools, the HTTP server, the browser page, the EC2 deployment wrapper, and the Lambda handler.

### Fields
- `sku` - unique stock keeping unit string used to identify the item.
- `description` - human-readable item description.
- `bin_location` - warehouse bin identifier where the item is stored.
- `quantity` - on-hand count stored as a non-negative integer.
- `unit` - quantity unit string such as `each` or `roll`.

### Notes
- The CLI validates that these required fields are present before it lists or finds items.
- The HTTP server returns this same JSON structure unchanged at `GET /inventory`.
- The browser page fetches the same JSON structure and renders it as a table.
- The EC2 deployment wrapper does not change the JSON contract; it only changes where the same HTTP process is started.
- The Lambda handler returns the same inventory JSON contract from a different compute boundary.
- The JSON file remains the canonical interchange format for this stage.
