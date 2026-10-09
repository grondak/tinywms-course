# TinyWMS architecture

## Current architecture
- TinyWMS now has two relational deployment stories for the same schema: a self-managed Linux database and an Amazon RDS database.
- The logical tables, keys, and JSON-to-table mapping stay the same as the previous lesson.
- The goal of this stage is operational comparison: students should see which tasks they do themselves on Linux and which tasks AWS does for them with RDS.
- Lambda and API Gateway still do not read from the database in this stage.

## Deployment variants
### Raspberry Pi Linux
- The Pi remains a teaching host for ordinary Linux processes, files, and ports.
- The Pi is not the relational database focus in this lesson, but students may still run other TinyWMS components there.

### EC2 Linux
- Students can run the application or the database on EC2 when they want a Linux host they fully manage.
- They are responsible for starting the process, opening the port, backing up data, and stopping the instance.
- This is the baseline comparison point for RDS.

### Self-managed relational database on Linux
- Students install and operate PostgreSQL or MariaDB themselves.
- They choose the port, manage the service, monitor the process, and clean up local data files.
- The schema in `data/schema.sql` and the seed rows in `data/seed.sql` remain unchanged.

### Amazon RDS
- AWS manages the database process, patching, and underlying host for the student.
- Students still own the schema, seed data, credentials, security group access, and cost control.
- The database logical design is unchanged; only the hosting and operations boundary moves.

### Lambda and API Gateway
- These stages still exist in the repository, but they have not been converted to use RDS yet.
- The purpose of this stage is to prepare for that later change without mixing the responsibilities together.

## What stayed the same
- The inventory JSON contract stayed the same.
- The relational schema stayed the same.
- The JSON-to-table mapping stayed the same.
- The meaning of SKU, description, bin, quantity, and unit stayed the same.

## What moved to AWS with RDS
- Database host provisioning
- Database software patching
- Underlying machine and storage maintenance
- Some monitoring responsibilities

## What students still control
- Schema creation
- Seed loading
- Credentials and secret handling
- Network access controls
- Cost cleanup and deletion

## Architecture History
- Stage 0: repository scaffold only.
- Stage 1: JSON inventory contract and CLI reader.
- Stage 2: Linux-visible command-line examples.
- Stage 3: Raspberry Pi / EC2-style HTTP server added.
- Stage 4: browser client added.
- Stage 5: EC2 deployment scripts and documentation added without changing the app contract.
- Stage 6: Lambda implementation added alongside the existing Linux server path.
- Stage 7: API Gateway added in front of Lambda without changing the inventory contract.
- Stage 8: relational schema and JSON-to-table mapping added while preserving the existing inventory contract.
- Stage 9: Amazon RDS added as a managed deployment option for the same relational schema.
