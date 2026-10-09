import json
import unittest
from pathlib import Path


class RdsTemplateTests(unittest.TestCase):
    def test_template_mentions_postgres_and_schema(self):
        template = json.loads(Path('deploy/rds/template.json').read_text(encoding='utf-8'))
        self.assertEqual(template['Resources']['TinyWmsDatabase']['Properties']['Engine'], 'postgres')
        self.assertEqual(template['Resources']['TinyWmsDatabase']['Properties']['DBName']['Ref'], 'DatabaseName')

    def test_bootstrap_contains_same_tables(self):
        bootstrap = Path('deploy/rds/bootstrap.sql').read_text(encoding='utf-8')
        self.assertIn('CREATE TABLE products', bootstrap)
        self.assertIn('CREATE TABLE inventory_locations', bootstrap)
        self.assertIn('CREATE TABLE orders', bootstrap)
        self.assertIn('CREATE TABLE order_lines', bootstrap)

    def test_lambda_rds_template_exposes_optional_sqs_queue_url(self):
        template = json.loads(Path('deploy/lambda-rds/template.json').read_text(encoding='utf-8'))
        self.assertIn('PickWorkQueueUrl', template['Parameters'])
        env = template['Resources']['TinyWmsInventoryFunction']['Properties']['Environment']['Variables']
        self.assertEqual(env['TINYWMS_SQS_QUEUE_URL']['Ref'], 'PickWorkQueueUrl')


if __name__ == '__main__':
    unittest.main()
