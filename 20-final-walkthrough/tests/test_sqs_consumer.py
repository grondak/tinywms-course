import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from src import sqs_consumer


class SqsConsumerTests(unittest.TestCase):
    def test_parse_receive_message_response_extracts_message_and_attributes(self):
        xml_text = """
        <ReceiveMessageResponse>
          <ReceiveMessageResult>
            <Message>
              <MessageId>abc-123</MessageId>
              <ReceiptHandle>handle-1</ReceiptHandle>
              <Body>{"messageType":"PickWorkRequested"}</Body>
              <Attribute>
                <Name>ApproximateReceiveCount</Name>
                <Value>2</Value>
              </Attribute>
            </Message>
          </ReceiveMessageResult>
        </ReceiveMessageResponse>
        """
        messages = sqs_consumer.parse_receive_message_response(xml_text)
        self.assertEqual(messages[0]["MessageId"], "abc-123")
        self.assertEqual(messages[0]["attributes"]["ApproximateReceiveCount"], "2")

    def test_print_message_without_ack_leaves_message_for_retry(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            sqs_consumer.print_message(
                {
                    "MessageId": "abc-123",
                    "ReceiptHandle": "handle-1",
                    "Body": '{"messageType":"PickWorkRequested"}',
                    "attributes": {"ApproximateReceiveCount": "1"},
                },
                ack=False,
            )
        output = buffer.getvalue()
        self.assertIn('"messageId": "abc-123"', output)
        self.assertIn('PickWorkRequested', output)
        self.assertIn('left messageId=abc-123 on queue for retry', output)

    def test_print_message_with_ack_deletes_message(self):
        buffer = io.StringIO()
        with mock.patch("src.sqs_consumer.delete_message") as delete_message, redirect_stdout(buffer):
            sqs_consumer.print_message(
                {
                    "MessageId": "abc-123",
                    "ReceiptHandle": "handle-1",
                    "Body": '{"messageType":"PickWorkRequested"}',
                    "attributes": {"ApproximateReceiveCount": "3"},
                },
                ack=True,
            )
        delete_message.assert_called_once_with("handle-1")
        self.assertIn('acknowledged messageId=abc-123', buffer.getvalue())

    def test_main_prints_no_messages(self):
        buffer = io.StringIO()
        with mock.patch("src.sqs_consumer.receive_messages", return_value=[]), redirect_stdout(buffer):
            code = sqs_consumer.main(["sqs_consumer.py"])
        self.assertEqual(code, 0)
        self.assertIn("no messages available", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
