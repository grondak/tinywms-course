import io
import json
import unittest
from contextlib import redirect_stdout
from unittest import mock

from src import sqs_publish


class FakeResponse:
    def __init__(self, body_text):
        self.body_text = body_text

    def read(self):
        return self.body_text.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class SqsPublishTests(unittest.TestCase):
    def test_publish_json_message_posts_body_and_returns_message_id(self):
        response_xml = """
        <SendMessageResponse>
          <SendMessageResult>
            <MessageId>msg-123</MessageId>
          </SendMessageResult>
        </SendMessageResponse>
        """
        buffer = io.StringIO()
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(response_xml)) as urlopen, redirect_stdout(buffer):
            result = sqs_publish.publish_json_message(
                "https://sqs.example.amazonaws.com/123/tinywms-pick-work",
                {"messageType": "PickWorkRequested", "orderId": 7},
            )
        self.assertEqual(result["messageId"], "msg-123")
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://sqs.example.amazonaws.com/123/tinywms-pick-work")
        self.assertIn("published messageId=msg-123", buffer.getvalue())
        self.assertIn('"orderId": 7', result["body"])

    def test_publish_raises_when_message_id_missing(self):
        response_xml = "<SendMessageResponse><SendMessageResult></SendMessageResult></SendMessageResponse>"
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(response_xml)):
            with self.assertRaises(RuntimeError):
                sqs_publish.publish_json_message("https://example.com/queue", {"messageType": "PickWorkRequested"})


if __name__ == "__main__":
    unittest.main()
