# TinyWMS Git milestones

## Purpose
This document turns the repository history into a teaching map.

Students should be able to check out an earlier milestone and see the simpler architecture that really existed then, rather than a final architecture copied backward into every point in time.

## Suggested milestone tags
Create annotated tags only after the repository history for that stage has been accepted.

| Tag | Course stage(s) | What students should see after checkout |
| --- | --- | --- |
| `lesson-01-json-cli` | Stage 1 | inventory JSON examples, schema, and CLI inspection tools |
| `lesson-03-pi-http` | Stage 3 | smallest visible Python HTTP server returning `GET /inventory` |
| `lesson-04-browser` | Stage 4 | plain HTML/CSS/JS browser page using `fetch()` against the inventory API |
| `lesson-05-ec2-http` | Stage 5 | same HTTP behavior plus EC2 deployment guidance |
| `lesson-06-lambda` | Stage 6 | Lambda implementation alongside earlier Linux-hosted path |
| `lesson-07-api-gateway` | Stage 7 | API Gateway in front of Lambda with unchanged inventory JSON behavior |
| `lesson-08-relational-db` | Stage 8 | relational schema, seed SQL, and JSON-to-table mapping |
| `lesson-09-rds` | Stage 9 | RDS deployment option for the same relational schema |
| `lesson-12-transactional-orders` | Stages 11-12 | `POST /orders`, transactional inventory decrement, and concurrency fix |
| `lesson-14-queue-event` | Stages 13-14 | SQS pick-work command and EventBridge `OrderPlaced` event |
| `lesson-15-pick-ticket-worker` | Stage 15 | long-running Linux worker writing human-readable pick tickets |
| `lesson-17-container-worker` | Stage 17 | same worker packaged in Docker |
| `lesson-18-aws-deployment` | Stage 18 | reproducible CloudFormation deployment for the cloud-side architecture |

## Why some tags skip numbers
The milestone names are based on major teaching checkpoints, not every single stage directory number.

For example:
- Stage 2 adds Linux visibility but does not replace the JSON CLI story, so the first major runtime milestone is still the JSON CLI checkpoint.
- Stages 11 and 12 are grouped into `lesson-12-transactional-orders` because the teaching goal is a complete order path with visible rollback and concurrency protection.
- Stages 13 and 14 are grouped into `lesson-14-queue-event` because students should compare command and event messaging together.

If your course wants one tag per stage, you may create more tags. This document names the minimum major milestones required by the lesson prompt.

## How to create the milestone tags
List recent commits so you can find the right checkpoints:
```bash
git log --oneline --decorate --graph
```

Create annotated tags on the commits that match the accepted stage boundaries:
```bash
git tag -a lesson-01-json-cli <commit> -m "Stage 1: JSON CLI backbone"
git tag -a lesson-03-pi-http <commit> -m "Stage 3: Raspberry Pi HTTP server"
git tag -a lesson-04-browser <commit> -m "Stage 4: browser inventory page"
git tag -a lesson-05-ec2-http <commit> -m "Stage 5: EC2 deployment path"
git tag -a lesson-06-lambda <commit> -m "Stage 6: Lambda inventory"
git tag -a lesson-07-api-gateway <commit> -m "Stage 7: API Gateway"
git tag -a lesson-08-relational-db <commit> -m "Stage 8: relational persistence"
git tag -a lesson-09-rds <commit> -m "Stage 9: RDS option"
git tag -a lesson-12-transactional-orders <commit> -m "Stages 11-12: orders and concurrency"
git tag -a lesson-14-queue-event <commit> -m "Stages 13-14: queue and event"
git tag -a lesson-15-pick-ticket-worker <commit> -m "Stage 15: pick-ticket worker"
git tag -a lesson-17-container-worker <commit> -m "Stage 17: worker container"
git tag -a lesson-18-aws-deployment <commit> -m "Stage 18: AWS deployment"
```

Inspect a tag before sharing it:
```bash
git show lesson-03-pi-http --stat
```

Push the tags:
```bash
git push origin --tags
```

## How students should use the milestones
Fetch tags if they are missing locally:
```bash
git fetch --tags
```

List the available lesson milestones:
```bash
git tag --list 'lesson-*'
```

Check out one milestone:
```bash
git checkout lesson-01-json-cli
```

Or with newer Git advice:
```bash
git switch --detach lesson-01-json-cli
```

Return to the previous branch:
```bash
git switch -
```

## Verification commands by milestone
These commands are intentionally small. The goal is to prove that each milestone exposes the simpler architecture expected for that time.

### `lesson-01-json-cli`
Expected concept: JSON files and CLI tools before HTTP.
```bash
python3 src/inventory_cli.py list data/inventory.json
python3 -m unittest discover -s tests
```

### `lesson-03-pi-http`
Expected concept: visible Linux HTTP server on a port.
```bash
TINYWMS_PORT=8000 python3 src/http_server.py data/inventory.json
curl http://localhost:8000/inventory
```

### `lesson-04-browser`
Expected concept: browser fetches the same inventory JSON contract.
```bash
TINYWMS_PORT=8000 python3 src/http_server.py data/inventory.json
# Then open http://localhost:8000/ in a browser
```

### `lesson-05-ec2-http`
Expected concept: same app contract, different host and operator boundary.
```bash
cat deploy/ec2/start.sh
cat deploy/ec2/tinywms.service
```

### `lesson-06-lambda`
Expected concept: Lambda execution model appears without deleting the Linux path.
```bash
./deploy/lambda/invoke.sh
python3 -m unittest discover -s tests
```

### `lesson-07-api-gateway`
Expected concept: API Gateway forwards HTTP to Lambda.
```bash
cat deploy/apigateway/template.json
./deploy/apigateway/invoke.sh
```

### `lesson-08-relational-db`
Expected concept: relational schema derived from earlier JSON contracts.
```bash
cat data/schema.sql
python3 data/load_from_json.py data/inventory.json
```

### `lesson-09-rds`
Expected concept: the same schema can move to managed RDS.
```bash
cat deploy/rds/template.json
cat deploy/rds/bootstrap.sql
```

### `lesson-12-transactional-orders`
Expected concept: orders commit transactionally and concurrency is visible.
```bash
python3 src/concurrency_demo.py naive
python3 src/concurrency_demo.py fixed
```

### `lesson-14-queue-event`
Expected concept: compare command messaging with domain events.
```bash
cat data/pick-work-message-example.json
cat data/order-placed-event-example.json
python3 deploy/events/run-shipping-consumer.sh
python3 deploy/events/run-audit-consumer.sh
```

### `lesson-15-pick-ticket-worker`
Expected concept: long-running Linux worker writes a human-readable file.
```bash
python3 src/pick_ticket_worker.py --once --message-file data/pick-work-message-example.json --output pick-tickets.txt
cat pick-tickets.txt
```

### `lesson-17-container-worker`
Expected concept: the same worker process now runs in a container.
```bash
docker build -f Dockerfile.worker -t tinywms-pick-ticket-worker:lesson .
./deploy/container/run-worker-container.sh --once --message-file data/pick-work-message-example.json
```

### `lesson-18-aws-deployment`
Expected concept: the current cloud architecture is reproducibly deployable.
```bash
python3 deploy/aws/package_lambda.py build/tinywms-lambda.zip
python3 -m unittest discover -s tests
```

## Continuity checklist for tag review
Before finalizing a tag, confirm all four:
1. The checked-out code matches the simpler architecture students are supposed to see.
2. The README at that milestone gives commands that make sense for that milestone.
3. The inherited contracts still mean what the stage says they mean.
4. The verification command for that milestone succeeds or at least fails in a useful, understandable way.

## Common mistakes to avoid
- Do not retag every milestone to the latest commit.
- Do not move older milestone tags forward just because the newest architecture is more complete.
- Do not delete older runtime paths when later ones are added if the course is trying to preserve comparison.
- Do not assume all stages should run the latest cloud deployment commands.
- Do not commit secrets while creating milestone examples or deployment parameter files.

## Cleanup
Delete a local tag if you pointed it at the wrong commit:
```bash
git tag -d lesson-03-pi-http
```

Delete a remote tag only if you must correct a mistake and after warning students:
```bash
git push origin :refs/tags/lesson-03-pi-http
```
