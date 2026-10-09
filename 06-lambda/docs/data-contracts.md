# TinyWMS data contracts

## Inventory JSON document
TinyWMS uses one top-level JSON object containing an `inventory` array.

### Fields
- `inventory` - array of product records
- `inventory[].sku` - stable product identifier used by CLI, HTTP, browser, and Lambda examples
- `inventory[].description` - human-readable product description
- `inventory[].bin` - warehouse bin or shelf location
- `inventory[].quantity` - on-hand count as a non-negative integer
- `inventory[].unit` - unit of measure such as `each`, `box`, or `case`

## Lambda event and response shape
The Lambda example keeps the request and response visible as JSON.

### Request fields
- `httpMethod` - expected to be `GET`
- `path` - expected to be `/inventory`
- `queryStringParameters` - optional request parameters, kept visible for teaching even when unused

### Response fields
- `statusCode` - HTTP-style numeric status code
- `headers` - response headers as a JSON object
- `body` - JSON string containing the inventory payload or an error object
- `isBase64Encoded` - boolean flag kept explicit in the example response

## Notes
- This contract is intentionally small so beginning students can understand it immediately.
- Later stages must preserve this JSON meaning unless a lesson explicitly says otherwise.
