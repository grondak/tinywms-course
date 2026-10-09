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


if __name__ == '__main__':
    unittest.main()
