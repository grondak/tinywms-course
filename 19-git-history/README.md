# TinyWMS lesson: 19-git-history

## Stage purpose
This stage teaches students to use Git history as part of the system architecture story. Instead of treating the repository as only the final AWS version, students can check out named milestones and see the simpler JSON CLI, Pi HTTP server, browser, Lambda, database, queue/event, worker, and container stages as they actually existed.

## Files in this lesson
- `README.md` - this lesson guide for creating and using milestone tags in the TinyWMS teaching repository
- `docs/architecture.md` - updated architecture guide explaining how Git milestones preserve the semester's architecture history
- `docs/git-milestones.md` - milestone/tag map with suggested tag names, what each checkpoint represents, and how to verify each one after checkout
- `docs/data-contracts.md` - updated to note that Git milestones preserve changing implementations while keeping visible contracts understandable across stages
- `tests/test_git_milestones_doc.py` - tests that validate the milestone document covers the major teaching checkpoints named in this lesson

## Run the lesson
From this folder:
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

Review the milestone map:
```bash
cat docs/git-milestones.md
```

Create the recommended annotated tags after you confirm the repository history lines up with your accepted stages:
```bash
git tag -a lesson-01-json-cli -m "Stage 1: JSON CLI backbone"
git tag -a lesson-03-pi-http -m "Stage 3: Raspberry Pi HTTP server"
git tag -a lesson-05-ec2-http -m "Stage 5: EC2 deployment path"
git tag -a lesson-04-browser -m "Stage 4: browser inventory page"
git tag -a lesson-06-lambda -m "Stage 6: Lambda inventory"
git tag -a lesson-07-api-gateway -m "Stage 7: API Gateway in front of Lambda"
git tag -a lesson-08-relational-db -m "Stage 8: relational schema and mapping"
git tag -a lesson-09-rds -m "Stage 9: RDS deployment option"
git tag -a lesson-12-transactional-orders -m "Stages 11-12: orders and concurrency control"
git tag -a lesson-14-queue-event -m "Stages 13-14: SQS command and EventBridge event"
git tag -a lesson-15-pick-ticket-worker -m "Stage 15: pick-ticket worker"
git tag -a lesson-17-container-worker -m "Stage 17: containerized worker"
git tag -a lesson-18-aws-deployment -m "Stage 18: reproducible AWS deployment"
```

List the tags:
```bash
git tag --list 'lesson-*'
```

Check out one milestone in detached HEAD mode and inspect it:
```bash
git checkout lesson-03-pi-http
ls
python3 -m unittest discover -s tests
```

Return to your working branch:
```bash
git switch -
```

Push tags to a remote when you are ready:
```bash
git push origin --tags
```

## Run tests
```bash
python3 -m unittest discover -s tests
node --test tests/test_web_app.js
```

## Student exercises
1. Check out `lesson-03-pi-http` and `lesson-18-aws-deployment` one at a time. For each checkout, identify where the code is running, where the data is stored, and which boundaries are JSON, HTTP, SQL, or AWS resources.
2. Create one additional local annotated tag for a milestone you personally found important, such as the callback demo stage, then write one verification command you would run after checking it out.

## Continuity note
- Inherited contract: the application code, JSON contracts, SQL schema meaning, SQS message, EventBridge event, and worker output all remain byte-for-byte compatible with the previous stage
- Boundary changed in this stage: the repository now explicitly documents Git milestones so students can move across time and inspect earlier architectural boundaries instead of only reading about them

## Cleanup
No external resources are created in this stage.

If you created local tags that you do not want to keep yet:
```bash
git tag -d lesson-01-json-cli lesson-03-pi-http lesson-05-ec2-http lesson-04-browser lesson-06-lambda lesson-07-api-gateway lesson-08-relational-db lesson-09-rds lesson-12-transactional-orders lesson-14-queue-event lesson-15-pick-ticket-worker lesson-17-container-worker lesson-18-aws-deployment
```
