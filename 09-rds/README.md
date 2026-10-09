# TinyWMS lesson: 09-rds

## Stage purpose
This stage adds an Amazon RDS deployment path for the relational TinyWMS database while keeping the same schema and the same JSON-to-table meaning from the previous lesson. Students can compare self-managed Linux database operations with managed AWS database operations and see what responsibilities moved to AWS.

## Files in this lesson
- `data/schema.sql` - unchanged logical schema for products and inventory locations
- `data/seed.sql` - sample seed data that still matches the JSON inventory contract
- `data/load_from_json.py` - converts the JSON inventory sample into SQL seed statements
- `deploy/rds/parameters.example.json` - sample CloudFormation parameters showing which values students must supply
- `deploy/rds/template.json` - minimal RDS deployment template for the existing relational database
- `deploy/rds/bootstrap.sql` - database initialization SQL used after the RDS instance is available
- `deploy/rds/connect.sh` - helper showing how to connect to the RDS endpoint from a Linux shell
- `docs/architecture.md` - compares self-managed Linux DB versus managed RDS and explains the boundary shift
- `docs/data-contracts.md` - keeps the JSON-to-relational mapping explicit
- `tests/test_rds_template.py` - checks that the deployment template still references the relational schema conceptually

## Run the lesson
From this folder:
```bash
python3 data/load_from_json.py data/inventory.json
python3 -m json.tool deploy/rds/parameters.example.json
```
To inspect the RDS deployment artifacts, open `deploy/rds/template.json` and `deploy/rds/bootstrap.sql` in an editor. The template is meant to be read before it is ever deployed.

## Run tests
```bash
python3 -m unittest discover -s tests
```

## Student exercises
1. Change one product description in `data/inventory.json`, regenerate the SQL seed output, and confirm the relational schema still does not need to change.
2. Edit `deploy/rds/parameters.example.json` to model a different DB instance class, then explain in `docs/architecture.md` which responsibility changed and which did not.

## Continuity note
- Inherited contract: the inventory JSON document and the relational schema meaning from stage 8 remain the same
- Boundary changed in this stage: the relational database can now be deployed as Amazon RDS instead of only on a self-managed Linux host

## Cleanup
No AWS resources are created just by reading or testing this repository. If you deploy the template to AWS, delete the RDS instance, any subnet group, security group, and any stack resources you created to avoid ongoing charges.
