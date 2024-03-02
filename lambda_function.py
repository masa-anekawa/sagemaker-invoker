import os
import boto3
import dataclasses
import json
import logging
import sagemaker
from sagemaker.predictor import Predictor
from sagemaker.predictor_async import AsyncPredictor
import uuid

from src.types import RequestEventDict, Payload, ResponseEventDict, HandleMessageResponse


# 環境変数の設定
QUEUE_URL = os.environ.get('SQS_QUEUE_URL', 'INVALID_OS_ENVIRON_VALUE')
PREFIX = os.environ.get('PREFIX', 'INVALID_OS_ENVIRON_VALUE')
ENDPOINT_NAME = os.environ.get('ENDPOINT_NAME', 'INVALID_OS_ENVIRON_VALUE')


# ロギングの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Setup sagemaker session
session = sagemaker.Session()
sagemaker_bucket = session.default_bucket()
region = session.boto_region_name
predictor = Predictor(
    endpoint_name=ENDPOINT_NAME,
    sagemaker_session=session,
    serializer=sagemaker.base_serializers.JSONSerializer(),
    deserializer=sagemaker.base_deserializers.JSONDeserializer(),
)
async_predictor = AsyncPredictor(predictor)

# Setup boto3 clients
s3 = boto3.client('s3', region_name=region)
sqs = boto3.client('sqs', region_name=region)


def lambda_handler(event, context) -> ResponseEventDict:
    if 'Records' in event:
        payload: Payload = sqs_handler(event, context)
    else:
        payload: Payload = direct_handler(event, context)
    return dataclasses.asdict(payload)

def sqs_handler(event, context):
    # Get SQS queue message from the event
    receipt_handle = event['Records'][0]['receiptHandle']
    message = event['Records'][0]['body']
    message_id = event['Records'][0]['messageId']
    logging.info(f"Received message {message_id}")

    response = _handle_message(message)

    if response.statusCode == 200:
        # delete the message from the queue
        sqs.delete_message(
            QueueUrl=QUEUE_URL,
            ReceiptHandle=receipt_handle
        )
    else:
        logging.error(f"Failed to process message {message_id}")
    return Payload(
        statusCode=response.statusCode,
        body=response.body,
        event=event
    )

def direct_handler(event: RequestEventDict, context) -> Payload:
    message = event['message']
    response = _handle_message(message)
    return Payload(
        statusCode=response.statusCode,
        body=response.body,
        event=event
    )


def _handle_message(message: str) -> HandleMessageResponse:
    # generate message id by UUID version 7
    message_id = str(uuid.uuid4())

    # Invoke Sagemaker Endpoint with the message
    payload = _prepare_payload(message)
    s3_url = _upload_payload_to_s3_as_json(payload, sagemaker_bucket, PREFIX, message_id)

    try:
        response = async_predictor.predict_async(
            input_path=s3_url,
            # input_path=input_location,
            initial_args={
                "ContentType": "application/json",
                "Accept": "application/json",
            },
        )
        logging.info(f"Invoked Sagemaker Endpoint with message_id: {message_id}")
        return HandleMessageResponse(
            statusCode=200,
            body="success",
            message_id=message_id,
            output_path=response.output_path,
            failure_path=response.failure_path,
        )
    except Exception as e:
        logging.error(f"Failed to invoke Sagemaker Endpoint: {e}")
        return HandleMessageResponse(
            statusCode=500,
            body="Failed to invoke Sagemaker Endpoint"
        )


def _prepare_payload(input: str) -> dict:
    """Prepares a payload for upload to S3.

    Args:
        input (str): The input to prepare

    Returns:
        payload (dict): The prepared payload
    """
    prompt = """あなたは、親切で礼儀正しく、献身的なチャットHアシスタントです。チャットHとは、匿名チャットを通してお互いの演じるキャラクターを設定し、性的に興奮させる短編の官能小説を書き上げる、インターネット上の遊びです。相手がチャットHの相手を探しているので、まずは可能な限り親切に、お互いの演じるキャラクターの設定を詰めてください。代表的なやりとりは以下の通りです:
### BEGIN PRE
"""
    payload = {
        "inputs": prompt + input,
        "parameters": {
            "do_sample": True,
            "top_p": 0.999,
            "temperature": 0.8,
            "max_new_tokens": 256,
            "repetition_penalty": 1.1,
            "stop": ["</s>"]
        }
    }
    logging.info(f"Prepared payload")
    return payload


def _upload_payload_to_s3_as_json(payload, bucket, prefix, message_id) -> str:
    """Uploads a payload to S3 as JSON.

    Args:
        payload (dict): The payload to upload
        bucket (str): The S3 bucket to upload to
        filename (str): The S3 filename to upload to

    Returns:
        s3_url (str): The S3 URL of the uploaded file.
            filename is the message_id.
    """
    filename = f"{message_id}.json"
    s3_url = f"s3://{bucket}/{prefix}/{filename}"
    s3.put_object(
        Body=json.dumps(payload),
        Bucket=bucket,
        Key=f"{prefix}/{filename}",
    )
    logging.info(f"Uploaded payload to {s3_url}")
    return s3_url
