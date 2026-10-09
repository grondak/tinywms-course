# TinyWMS data contracts

## Inventory JSON document
TinyWMS uses one top-level JSON object containing an `inventory` array.

### Fields
- `inventory` - array of product records
- `inventory[].sku` - stable product identifier used by CLI, HTTP, browser, Lambda, and API Gateway examples
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

## API Gateway request path
When API Gateway fronts Lambda, the gateway request is still readable as JSON inside the Lambda event.

### Gateway-visible request fields
- `resource` - API Gateway route pattern such as `/inventory`
- `path` - concrete request path seen by the event
- `httpMethod` - expected to be `GET`
- `headers` - request headers as JSON
- `queryStringParameters` - optional request parameters
- `body` - request body, which is empty for `GET /inventory`

### Gateway-visible response fields
- `statusCode` - numeric response sent back through API Gateway
- `headers` - response headers as JSON
- `body` - inventory JSON string returned unchanged to the browser or curl client
- `isBase64Encoded` - explicit encoding flag

## Notes
- This contract is intentionally small so beginning students can understand it immediately.
- Later stages must preserve this JSON meaning unless a lesson explicitly says otherwise.
