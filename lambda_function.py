import os
import boto3
import logging

from io import BytesIO

# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

sqs = boto3.client('sqs')


def lambda_handler(event, context):
    # Get SQS queue message from the event
    queue_url = os.environ['SQS_QUEUE_URL']
    receipt_handle = event['Records'][0]['receiptHandle']
    message = event['Records'][0]['body']

    response = {
        'statusCode': 200,
        'body': f'Successfully received "{message}".'
    }
    # delete the message from the queue
    sqs.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
    )
    logger.info(response)
    return response


def lambda_handler_local(event, context):
    input_file_key = './input_format.csv'
    output_file_key = './output/output_format.csv'

    response = {
        'statusCode': 200,
        'body': f'Successfully transformed {input_file_key} and saved as {output_file_key}'
    }
    logger.info(response)
    return response
