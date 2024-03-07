from unittest.mock import patch, MagicMock
import unittest
from unittest.mock import patch, ANY, call

from src.types import HandleMessageResponse, RequestEventDict, ResponseEventDict, Payload

import lambda_function


BODY_FAILURE = "Failed to invoke Sagemaker Endpoint"
BODY_SUCCESS = "success"
EXCEPTION_MESSAGE = "test exception"
FAILURE_PATH = "failure_path"
INPUT_MESSAGE = "test message"
MESSAGE_ID = "test_message_id"
OUTPUT_PATH = "output_path"
S3_UPLOADED_URI = "s3://test_bucket/test_key"


class TestHandleMessage(unittest.TestCase):
    @patch('lambda_function._prepare_payload')
    @patch('lambda_function._upload_payload_to_s3_as_json')
    @patch('lambda_function.async_predictor.predict_async')
    def test_handle_message_success(self, mock_predict_async, mock_upload_to_s3, mock_prepare_payload):
        # Arrange
        mock_message = "test message"
        mock_prepare_payload.return_value = {}
        mock_upload_to_s3.return_value = S3_UPLOADED_URI
        mock_predict_async.return_value.output_path = OUTPUT_PATH
        mock_predict_async.return_value.failure_path = FAILURE_PATH

        # Act
        handle_message_response = lambda_function._handle_message(mock_message)

        # Assert
        self.assertEqual(handle_message_response.statusCode, 200)
        self.assertEqual(handle_message_response.body, BODY_SUCCESS)
        self.assertEqual(handle_message_response.output_path, OUTPUT_PATH)
        self.assertEqual(handle_message_response.failure_path, FAILURE_PATH)

    @patch('lambda_function._prepare_payload')
    @patch('lambda_function._upload_payload_to_s3_as_json')
    @patch('lambda_function.async_predictor.predict_async')
    def test_handle_message_exception(self, mock_predict_async, mock_upload_to_s3, mock_prepare_payload):
        # Arrange
        mock_message = INPUT_MESSAGE
        mock_prepare_payload.return_value = {}
        mock_upload_to_s3.return_value = S3_UPLOADED_URI
        mock_predict_async.side_effect = Exception(EXCEPTION_MESSAGE)

        # Act
        handle_message_response = lambda_function._handle_message(mock_message)

        # Assert
        self.assertEqual(handle_message_response.statusCode, 500)
        self.assertEqual(handle_message_response.body, BODY_FAILURE)

    @patch('lambda_function._handle_message')
    def test_lambda_handler_direct_invocation_success(self, mock_handle_message):
        # Arrange
        mock_event = RequestEventDict(message=INPUT_MESSAGE)
        mock_context = {}
        mock_handle_message.return_value = HandleMessageResponse(statusCode=200, body=BODY_SUCCESS)
        # Act
        response = lambda_function.lambda_handler(mock_event, mock_context)
        # Assert
        mock_handle_message.assert_called_once_with(INPUT_MESSAGE)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], BODY_SUCCESS)

    @patch('lambda_function._handle_message')
    def test_lambda_handler_direct_invocation_failure(self, mock_handle_message):
        # Arrange
        mock_event = RequestEventDict(message=INPUT_MESSAGE)
        mock_context = {}
        mock_handle_message.return_value = HandleMessageResponse(statusCode=500, body=BODY_FAILURE)
        # Act
        response = lambda_function.lambda_handler(mock_event, mock_context)
        # Assert
        mock_handle_message.assert_called_once_with(INPUT_MESSAGE)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], BODY_FAILURE)

    @patch('lambda_function._handle_message')
    def test_lambda_handler_returns_json_serializable(self, mock_handle_message):
        # Arrange
        mock_event = RequestEventDict(message=INPUT_MESSAGE)
        mock_context = {}
        mock_handle_message.return_value = HandleMessageResponse(statusCode=200, body=BODY_SUCCESS, message_id=MESSAGE_ID)
        # Act
        response = lambda_function.lambda_handler(mock_event, mock_context)
        # Assert
        self.assertEqual(response, {
            "statusCode": 200,
            "body": BODY_SUCCESS,
            "event": {
                "message": INPUT_MESSAGE
            },
            "message_id": MESSAGE_ID
        })

if __name__ == '__main__':
    unittest.main()
