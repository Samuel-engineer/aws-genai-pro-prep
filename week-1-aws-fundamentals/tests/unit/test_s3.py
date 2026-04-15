import json
import os

import boto3
import pytest
from moto import mock_aws

from lambda_function import lambda_handler

BUCKET_NAME = "genai-prep-test-123456789"


class TestS3List:
    @mock_aws
    def test_list_empty_bucket(self, api_gateway_event_factory, lambda_context):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET_NAME)

        event = api_gateway_event_factory(
            method="GET",
            path="/s3/list",
            query_params={"bucket": BUCKET_NAME},
        )
        result = lambda_handler(event, lambda_context)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["objects"] == []

    @mock_aws
    def test_list_with_prefix(self, api_gateway_event_factory, lambda_context):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET_NAME)
        s3.put_object(Bucket=BUCKET_NAME, Key="docs/a.txt", Body=b"a")
        s3.put_object(Bucket=BUCKET_NAME, Key="images/b.png", Body=b"b")

        event = api_gateway_event_factory(
            method="GET",
            path="/s3/list",
            query_params={"bucket": BUCKET_NAME, "prefix": "docs/"},
        )
        result = lambda_handler(event, lambda_context)
        body = json.loads(result["body"])
        assert body["objects"] == ["docs/a.txt"]

    def test_list_missing_bucket_returns_400(self, api_gateway_event_factory, lambda_context):
        os.environ["S3_BUCKET"] = ""
        event = api_gateway_event_factory(
            method="GET",
            path="/s3/list",
        )
        result = lambda_handler(event, lambda_context)
        assert result["statusCode"] == 400


class TestS3Put:
    @mock_aws
    def test_put_then_list(self, api_gateway_event_factory, lambda_context):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET_NAME)

        put_event = api_gateway_event_factory(
            method="POST",
            path="/s3/put",
            body=json.dumps({
                "bucket": BUCKET_NAME,
                "key": "test/hello.txt",
                "content": "Bonjour GenAI",
            }),
        )
        put_result = lambda_handler(put_event, lambda_context)
        assert put_result["statusCode"] == 200

        list_event = api_gateway_event_factory(
            method="GET",
            path="/s3/list",
            query_params={"bucket": BUCKET_NAME, "prefix": "test/"},
        )
        list_result = lambda_handler(list_event, lambda_context)
        body = json.loads(list_result["body"])
        assert "test/hello.txt" in body["objects"]

    @mock_aws
    def test_put_content_is_correct(self, api_gateway_event_factory, lambda_context):
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=BUCKET_NAME)

        put_event = api_gateway_event_factory(
            method="POST",
            path="/s3/put",
            body=json.dumps({
                "bucket": BUCKET_NAME,
                "key": "docs/note.txt",
                "content": "Contenu de test",
            }),
        )
        lambda_handler(put_event, lambda_context)

        obj = s3.get_object(Bucket=BUCKET_NAME, Key="docs/note.txt")
        assert obj["Body"].read().decode("utf-8") == "Contenu de test"

    def test_put_missing_key_returns_400(self, api_gateway_event_factory, lambda_context):
        event = api_gateway_event_factory(
            method="POST",
            path="/s3/put",
            body=json.dumps({"bucket": BUCKET_NAME, "content": "data"}),
        )
        result = lambda_handler(event, lambda_context)
        assert result["statusCode"] == 400

    def test_put_missing_bucket_returns_400(self, api_gateway_event_factory, lambda_context):
        os.environ["S3_BUCKET"] = ""
        event = api_gateway_event_factory(
            method="POST",
            path="/s3/put",
            body=json.dumps({"key": "test.txt", "content": "data"}),
        )
        result = lambda_handler(event, lambda_context)
        assert result["statusCode"] == 400
