import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from src import eventbridge_publish


class FakeResponse:
    def __init__(self, body_text):
        self.body_text = body_text

    def read(self):
        return self.body_text.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class EventBridgePublishTests(unittest.TestCase):
    def test_publish_order_event_posts_body_and_returns_event_id(self):
        response_xml = """
        <PutEventsResponse>
          <PutEventsResult>
            <Entries>
              <member>
                <EventId>evt-123</EventId>
              </member>
            </Entries>
          </PutEventsResult>
        </PutEventsResponse>
        """
        buffer = io.StringIO()
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(response_xml)) as urlopen, redirect_stdout(buffer):
            result = eventbridge_publish.publish_order_event(
                {"eventType": "OrderPlaced", "orderId": 7, "customer": "Example School Store", "version": 1, "placedAt": "2026-01-15T10:30:00Z", "lines": []},
                "default",
            )
        self.assertEqual(result["eventId"], "evt-123")
        request = urlopen.call_args[0][0]
        self.assertEqual(request.full_url, "https://events.amazonaws.com/")
        self.assertIn("published eventId=evt-123", buffer.getvalue())
        self.assertIn('"orderId": 7', result["body"])
        self.assertEqual(result["eventBusName"], "default")

    def test_publish_raises_when_event_id_missing(self):
        response_xml = "<PutEventsResponse><PutEventsResult><Entries><member></member></Entries></PutEventsResult></PutEventsResponse>"
        with mock.patch("urllib.request.urlopen", return_value=FakeResponse(response_xml)):
            with self.assertRaises(RuntimeError):
                eventbridge_publish.publish_order_event(
                    {"eventType": "OrderPlaced", "orderId": 7, "customer": "Example School Store", "version": 1, "placedAt": "2026-01-15T10:30:00Z", "lines": []},
                    "default",
                )


if __name__ == "__main__":
    unittest.main()
