import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from deploy.aws import package_lambda


class AwsDeploymentFilesTests(unittest.TestCase):
    def test_cloudformation_template_includes_current_core_resources(self):
        template = json.loads(Path("deploy/aws/template.json").read_text(encoding="utf-8"))
        resources = template["Resources"]

        self.assertIn("TinyWmsInventoryFunction", resources)
        self.assertIn("TinyWmsInventoryApi", resources)
        self.assertIn("TinyWmsDatabase", resources)
        self.assertIn("TinyWmsPickWorkQueue", resources)
        self.assertIn("TinyWmsEventBus", resources)
        self.assertIn("TinyWmsLambdaExecutionRole", resources)

    def test_lambda_environment_wires_db_queue_and_event_bus(self):
        template = json.loads(Path("deploy/aws/template.json").read_text(encoding="utf-8"))
        env = template["Resources"]["TinyWmsInventoryFunction"]["Properties"]["Environment"]["Variables"]

        self.assertIn("TINYWMS_DB_HOST", env)
        self.assertIn("TINYWMS_DB_PORT", env)
        self.assertIn("TINYWMS_DB_NAME", env)
        self.assertIn("TINYWMS_DB_USER", env)
        self.assertIn("TINYWMS_DB_PASSWORD", env)
        self.assertIn("TINYWMS_SQS_QUEUE_URL", env)
        self.assertIn("TINYWMS_EVENT_BUS_NAME", env)

    def test_template_outputs_api_and_queue_details(self):
        template = json.loads(Path("deploy/aws/template.json").read_text(encoding="utf-8"))
        outputs = template["Outputs"]

        self.assertIn("ApiBaseUrl", outputs)
        self.assertIn("PickWorkQueueUrl", outputs)
        self.assertIn("DbEndpointAddress", outputs)
        self.assertIn("LambdaFunctionName", outputs)

    def test_package_lambda_creates_zip_with_handler_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            zip_path = Path(tmp) / "tinywms-lambda.zip"
            code = package_lambda.main(["package_lambda.py", str(zip_path)])
            self.assertEqual(code, 0)
            self.assertTrue(zip_path.exists())

            with zipfile.ZipFile(zip_path, "r") as zf:
                names = set(zf.namelist())

        self.assertIn("src/lambda_inventory.py", names)
        self.assertIn("src/order_service.py", names)
        self.assertIn("src/rds_inventory.py", names)
        self.assertIn("src/pick_work.py", names)
        self.assertIn("src/domain_events.py", names)

    def test_example_parameters_reference_artifact_bucket_and_code_key(self):
        parameters = json.loads(Path("deploy/aws/parameters.example.json").read_text(encoding="utf-8"))
        by_key = {entry["ParameterKey"]: entry["ParameterValue"] for entry in parameters}

        self.assertIn("ArtifactBucket", by_key)
        self.assertIn("LambdaCodeS3Key", by_key)
        self.assertIn("DatabasePassword", by_key)


if __name__ == "__main__":
    unittest.main()
