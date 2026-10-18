# TinyWMS Data Contracts

This document describes the TinyWMS inventory JSON contract.

## Inventory JSON

Inventory is stored as a JSON array of objects. Each object represents one stock item and is reused by the CLI, the Linux demo tools, and the HTTP server.

### Fields
- `sku` - unique stock keeping unit string used to identify the item.
- `description` - human-readable item description.
- `bin_location` - warehouse bin identifier where the item is stored.
- `quantity` - on-hand count stored as a non-negative integer.
- `unit` - quantity unit string such as `each` or `roll`.

### Notes
- The CLI validates that these required fields are present before it lists or finds items.
- The HTTP server returns this same JSON structure unchanged at `GET /inventory`.
- The JSON file remains the canonical interchange format for this stage.
