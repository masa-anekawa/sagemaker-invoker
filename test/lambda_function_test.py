import pandas as pd
from io import BytesIO
from unittest.mock import patch, ANY, call

import lambda_function


EVENT = {
    'Records': [
        {
            's3': {
                'bucket': {
                    'name': 'test-bucket'
                },
                'object': {
                    'key': 'test-key'
                }
            }
        }
    ]
}
INPUT_BYTES = 'input content\n'.encode()
OUTPUT_BYTES = 'output content\n'.encode()


def test_transform():
    # load df from csv files
    input_df = pd.read_csv('./input_format.csv')
    output_df = pd.read_csv('./output_format.csv')

    transformed_df = lambda_function.transform_df(input_df)

    # assert columns, row count, data types are equal between transform_df(input_df) and output_df
    assert list(transformed_df.columns) == list(output_df.columns)
    assert len(transformed_df) == len(output_df)
    assert transformed_df.dtypes.equals(output_df.dtypes)


@patch.object(lambda_function, 's3')
def test_lambda_handler_handles_input_and_output_with_s3(mock_s3):
    # Set up mock S3 response
    body_content = BytesIO(INPUT_BYTES)
    mock_response = {
        'Body': body_content
    }
    mock_s3.get_object.return_value = mock_response

    # mock transform_df
    def mock_transform_df(input_df):
        return pd.read_csv(BytesIO(OUTPUT_BYTES))
    lambda_function.transform_df = mock_transform_df

    # Call lambda_handler function
    lambda_function.lambda_handler(EVENT, None)

    # Assert that S3 client was called with correct arguments
    mock_s3.get_object.assert_called_once_with(Bucket='test-bucket', Key='test-key')
    mock_s3.put_object.assert_called_once_with(Bucket='warikan-san-csv-formatter-outputs', Key='test-key_formatted', Body=OUTPUT_BYTES)
