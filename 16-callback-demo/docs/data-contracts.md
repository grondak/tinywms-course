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

## Order request JSON document
TinyWMS orders use one top-level JSON object with a customer name and one or more requested lines.

### Fields
- `customer` - human-readable customer or class/store name submitting the order
- `lines` - array of requested order lines
- `lines[].sku` - product SKU being requested
- `lines[].quantity` - requested quantity as a positive integer

### Example
```json
{
  "customer": "Example School Store",
  "lines": [
    { "sku": "SKU-1001", "quantity": 2 },
    { "sku": "SKU-1003", "quantity": 1 }
  ]
}
```

## Order success response JSON document
A successful `POST /orders` returns a small JSON object describing what was committed.

### Fields
- `orderId` - database-generated order identifier
- `customer` - copied from the request
- `lines` - committed order lines
- `lines[].sku` - SKU that was written to `order_lines`
- `lines[].quantity` - quantity that was committed
- `status` - simple teaching field set to `created`

## Order failure response JSON document
The order path returns visible JSON errors rather than silent failures.

### Common fields
- `error` - short machine-readable error summary
- `details` - optional list or string explaining what was wrong

### Insufficient inventory failure
When requested quantity exceeds available stock, or when another concurrent transaction consumes the remaining stock first, the handler returns:
- `error` - `insufficient inventory`
- `sku` - SKU that could not be satisfied
- `requested` - requested quantity
- `available` - available quantity visible to the failing transaction at the time it detects the problem

## Pick-work SQS message JSON document
After a successful committed order, TinyWMS sends a separate JSON command message to Amazon SQS. This is not the HTTP response body and not a database row. It is the asynchronous handoff telling downstream work what to pick.

### Fields
- `messageType` - command type string, currently `PickWorkRequested`
- `version` - integer schema version for the message contract, currently `1`
- `orderId` - committed database order identifier
- `customer` - copied from the committed order
- `createdAt` - UTC timestamp string showing when the pick-work message was built
- `lines` - array of work lines to pick
- `lines[].lineNumber` - visible line ordering starting at `1`
- `lines[].sku` - SKU to pick
- `lines[].quantity` - quantity to pick

### Example
```json
{
  "messageType": "PickWorkRequested",
  "version": 1,
  "orderId": 42,
  "customer": "Example School Store",
  "createdAt": "2026-01-15T10:30:00Z",
  "lines": [
    { "lineNumber": 1, "sku": "SKU-1001", "quantity": 2 },
    { "lineNumber": 2, "sku": "SKU-1003", "quantity": 1 }
  ]
}
```

### Boundary note
- `POST /orders` still returns the established order success JSON contract to the caller.
- The SQS message is a second contract created after that order succeeds.
- The message intentionally contains enough order information for a downstream worker to act without re-reading the original HTTP request body.

## Pick-ticket text file document
The pick-ticket worker converts one `PickWorkRequested` JSON message into one human-readable text ticket appended to `pick-tickets.txt` on a Linux host.

### Fields represented in the text ticket
- `orderId` - shown in the ticket header so a human picker can match work to an order
- `customer` - shown in the ticket header for context
- `createdAt` - copied from the command so students can see when the asynchronous work request was created
- `lines[].sku` - shown per line item
- `lines[].quantity` - shown per line item
- product `description` - looked up for the SKU so the ticket is readable to a human worker
- inventory `bin` - looked up for the SKU so the picker knows where to go

### Example
```text
=== TinyWMS Pick Ticket ===
Order ID: 42
Customer: Example School Store
Requested At: 2026-01-15T10:30:00Z

1. SKU-1001 | Blue widget | qty 2 | bin A1-01
2. SKU-1003 | Packing tape | qty 1 | bin B2-04

```

### Boundary note
- The queue message remains the machine-readable contract between the order path and the worker.
- `pick-tickets.txt` is a downstream Linux file artifact created by the worker from that message.
- The file is intentionally human-readable rather than JSON so students can compare machine and human representations of the same work.

## OrderPlaced domain event JSON document
After a successful committed order, TinyWMS also emits a separate domain event to Amazon EventBridge. This contract is intentionally different from the SQS command. It describes something that already happened instead of instructing a specific downstream worker what to do.

### Fields
- `eventType` - event type string, currently `OrderPlaced`
- `version` - integer schema version for the event contract, currently `1`
- `orderId` - committed database order identifier
- `customer` - copied from the committed order
- `placedAt` - UTC timestamp string showing when the event document was built
- `lines` - array of committed order lines
- `lines[].lineNumber` - visible line ordering starting at `1`
- `lines[].sku` - SKU included in the committed order
- `lines[].quantity` - quantity included in the committed order

### Example
```json
{
  "eventType": "OrderPlaced",
  "version": 1,
  "orderId": 42,
  "customer": "Example School Store",
  "placedAt": "2026-01-15T10:30:00Z",
  "lines": [
    { "lineNumber": 1, "sku": "SKU-1001", "quantity": 2 },
    { "lineNumber": 2, "sku": "SKU-1003", "quantity": 1 }
  ]
}
```

### Command-versus-event note
- `PickWorkRequested` means: a downstream component is being told to do a specific task.
- `OrderPlaced` means: a business fact has occurred and any interested consumer may react.
- The command and the event can contain similar order information while serving different architectural roles.
- Keeping both contracts visible helps students compare imperative messaging and descriptive event publication.

## Callback demo boundary summary
This stage adds a teaching runbook for the complete callback path. The important idea is that one browser action produces several different visible representations.

### Browser to HTTP/API Gateway
- The browser sends the order request JSON document to `POST /orders`.
- The HTTP body is the same JSON shape described in **Order request JSON document**.

### API Gateway to Lambda
- API Gateway wraps the HTTP request in a Lambda proxy event JSON object.
- TinyWMS examples keep fields like `httpMethod`, `path`, `headers`, and `body` visible so students can inspect them directly.
- In this wrapped event, the original order JSON appears inside the `body` string.

### Lambda to RDS
- Lambda converts the request JSON into SQL operations against `orders`, `order_lines`, and `inventory_locations`.
- This boundary is not JSON on the wire; it is explicit SQL and relational rows.
- The demo should make clear that the committed database state changes before downstream asynchronous work is processed.

### Lambda to SQS
- After commit, Lambda builds the `PickWorkRequested` JSON command and sends it to SQS.
- This is the machine-readable command that the Python worker later consumes.

### Lambda to EventBridge
- After commit, Lambda also builds the `OrderPlaced` JSON event and sends it to EventBridge.
- This is a fact about the completed order, not an instruction to a specific worker.

### Python worker to Linux file
- The worker reads the `PickWorkRequested` JSON command.
- The worker writes a human-readable pick ticket to `pick-tickets.txt`.
- The callback demo intentionally ends on a plain Linux file so students can watch the result with `tail -f`.

## Relational mapping
The relational lessons keep the same inventory meaning but store it in tables.

### Table: `products`
- `sku` - primary key, copied from `inventory[].sku`
- `description` - copied from `inventory[].description`
- `unit` - copied from `inventory[].unit`

### Table: `inventory_locations`
- `sku` - foreign key to `products.sku`
- `bin` - copied from `inventory[].bin`
- `quantity` - copied from `inventory[].quantity`

### Table: `orders`
- `id` - generated order identifier returned as `orderId`
- `customer` - copied from order request `customer`
- `created_at` - database timestamp showing when the order row was inserted

### Table: `order_lines`
- `order_id` - foreign key to `orders.id`
- `line_number` - explicit visible line ordering
- `sku` - copied from request `lines[].sku`
- `quantity` - copied from request `lines[].quantity`

### RDS note
When the database is moved to Amazon RDS, the table structure and mapping do not change. Only the operational home of the same schema changes.

### Lambda-to-RDS note
When Lambda reads inventory from RDS, it must convert database rows back into the exact inventory JSON document shape. When Lambda writes orders to RDS, it must preserve the order request meaning while exposing success and failure as JSON.

## JSON-to-table mapping notes
- One JSON inventory item becomes one `products` row and one `inventory_locations` row.
- One order JSON document becomes one `orders` row and one or more `order_lines` rows.
- The order transaction must either write all related rows and decrements or write none of them.
- In the concurrency lesson, the visible SQL strategy is: insert the order row, then decrement inventory with a conditional `UPDATE` that succeeds only when enough quantity remains.
- In the SQS lesson, one committed order success result becomes one pick-work JSON message sent to the queue.
- In the pick-ticket worker lesson, that same pick-work message can become one appended human-readable ticket in `pick-tickets.txt`.
- In the domain-events lesson, that same committed order success result also becomes one `OrderPlaced` domain event sent to EventBridge.
- In the callback demo lesson, all of those boundary documents are intentionally shown side by side so students can compare them.
- The JSON documents remain the teaching contracts for application boundaries.
- SQL is used for persistence; Lambda reads SQL rows and emits JSON response bodies used by the earlier and current stages.

## Notes
- The model stays intentionally small so beginning students can understand it immediately.
- Later stages must preserve this JSON meaning unless a lesson explicitly says otherwise.
