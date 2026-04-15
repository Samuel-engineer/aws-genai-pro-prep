import json
import os
import sys
from dataclasses import dataclass, field

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

BUCKET_NAME = "genai-prep-test-123456789"


@dataclass
class FakeLambdaContext:
    """Mock Lambda context compatible with Powertools inject_lambda_context."""
    function_name: str = "MyFirstGenAIFunction"
    function_version: str = "$LATEST"
    invoked_function_arn: str = "arn:aws:lambda:us-east-1:123456789012:function:MyFirstGenAIFunction"
    memory_limit_in_mb: int = 256
    aws_request_id: str = "test-request-id"
    log_group_name: str = "/aws/lambda/MyFirstGenAIFunction"
    log_stream_name: str = "2026/04/15/[$LATEST]test"

    def get_remaining_time_in_millis(self) -> int:
        return 30000


@pytest.fixture
def lambda_context():
    return FakeLambdaContext()


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    """Configure les variables d'environnement pour tous les tests."""
    monkeypatch.setenv("S3_BUCKET", BUCKET_NAME)
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture
def api_gateway_event_factory():
    """Factory pour créer des événements API Gateway (format HTTP API)."""
    def _create_event(method="GET", path="/", query_params=None, body=None):
        return {
            "routeKey": f"{method} {path}",
            "rawPath": path,
            "rawQueryString": "",
            "headers": {
                "content-type": "application/json",
            },
            "requestContext": {
                "http": {
                    "method": method,
                    "path": path,
                    "protocol": "HTTP/1.1",
                    "sourceIp": "127.0.0.1",
                    "userAgent": "test",
                },
                "routeKey": f"{method} {path}",
                "stage": "$default",
                "timeEpoch": 1699564000000,
                "accountId": "123456789012",
                "apiId": "test-api",
                "domainName": "localhost",
                "domainPrefix": "localhost",
            },
            "queryStringParameters": query_params,
            "body": body,
            "isBase64Encoded": False,
        }
    return _create_event


@pytest.fixture
def mock_event_hello(api_gateway_event_factory):
    """Event GET /hello?name=Apprenti Pro"""
    event = api_gateway_event_factory(
        method="GET",
        path="/hello",
        query_params={"name": "Apprenti Pro"},
    )
    event["rawQueryString"] = "name=Apprenti+Pro"
    return event


@pytest.fixture
def mock_event_hello_no_name(api_gateway_event_factory):
    return api_gateway_event_factory(
        method="GET",
        path="/hello",
    )


@pytest.fixture
def load_event():
    """Factory fixture pour charger un event JSON depuis events/."""
    events_dir = os.path.join(os.path.dirname(__file__), "..", "..", "events")

    def _load(filename):
        with open(os.path.join(events_dir, filename)) as f:
            return json.load(f)

    return _load
