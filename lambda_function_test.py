from unittest.mock import patch, MagicMock
import unittest
from unittest.mock import patch, ANY, call

from src.types import HandleMessageResponse, RequestEvent, ResponseEvent

import lambda_function


class TestHandleMessage(unittest.TestCase):
    @patch('lambda_function._prepare_payload')
    @patch('lambda_function._upload_payload_to_s3_as_json')
    @patch('lambda_function.async_predictor.predict_async')
    def test_handle_message_success(self, mock_predict_async, mock_upload_to_s3, mock_prepare_payload):
        # Arrange
        mock_message = "test message"
        mock_prepare_payload.return_value = {}
        mock_upload_to_s3.return_value = "s3://test_bucket/test_key"
        mock_predict_async.return_value.output_path = "output_path"
        mock_predict_async.return_value.failure_path = "failure_path"

        # Act
        response = lambda_function._handle_message(mock_message)

        # Assert
        self.assertEqual(response.statusCode, 200)
        self.assertEqual(response.body, "success")
        self.assertEqual(response.output_path, "output_path")
        self.assertEqual(response.failure_path, "failure_path")

    @patch('lambda_function._prepare_payload')
    @patch('lambda_function._upload_payload_to_s3_as_json')
    @patch('lambda_function.async_predictor.predict_async')
    def test_handle_message_exception(self, mock_predict_async, mock_upload_to_s3, mock_prepare_payload):
        # Arrange
        mock_message = "test message"
        mock_prepare_payload.return_value = {}
        mock_upload_to_s3.return_value = "s3://test_bucket/test_key"
        mock_predict_async.side_effect = Exception("test exception")

        # Act
        response = lambda_function._handle_message(mock_message)

        # Assert
        self.assertEqual(response.statusCode, 500)
        self.assertEqual(response.body,
                         "Failed to invoke Sagemaker Endpoint")

    @patch('lambda_function._handle_message')
    def test_lambda_handler_direct_invocation_success(self, mock_handle_message):
        # Arrange
        mock_event = RequestEvent(message="test message")
        mock_context = {}
        mock_handle_message.return_value = HandleMessageResponse(statusCode=200, body="success")
        # Act
        response = lambda_function.lambda_handler(mock_event, mock_context)
        # Assert
        mock_handle_message.assert_called_once_with("test message")
        self.assertEqual(response.statusCode, 200)
        self.assertEqual(response.body, "success")


if __name__ == '__main__':
    unittest.main()
