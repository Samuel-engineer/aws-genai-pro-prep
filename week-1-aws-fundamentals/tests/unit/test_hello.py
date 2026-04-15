import json

from lambda_function import lambda_handler


class TestHello:
    def test_hello_with_name(self, mock_event_hello, lambda_context):
        result = lambda_handler(mock_event_hello, lambda_context)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["input_recu"] == "Apprenti Pro"
        assert "GenAI" in body["message"]

    def test_hello_default_name(self, mock_event_hello_no_name, lambda_context):
        result = lambda_handler(mock_event_hello_no_name, lambda_context)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["input_recu"] == "Inconnu"

    def test_hello_status_code(self, mock_event_hello, lambda_context):
        result = lambda_handler(mock_event_hello, lambda_context)
        assert result["statusCode"] == 200
        assert "body" in result

    def test_hello_from_event_file(self, load_event, api_gateway_event_factory, lambda_context):
        raw_event = load_event("hello_get.json")
        # Convert event to HTTP API format expected by Powertools
        event = api_gateway_event_factory(
            method="GET",
            path="/hello",
            query_params=raw_event.get("queryStringParameters"),
        )
        result = lambda_handler(event, lambda_context)
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["input_recu"] == "Apprenti Pro"
