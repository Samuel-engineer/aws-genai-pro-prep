"""
Tests d'intégration — nécessitent un stack SAM déployé.

Exécuter avec : pytest tests/integration/ -v -m integration

Ces tests sont ignorés par défaut (marqueur 'integration').
Pour les activer, déployer le stack et définir les variables :
    export API_ENDPOINT=https://xxx.execute-api.region.amazonaws.com/Prod
    export S3_BUCKET=genai-prep-dev-123456789
"""

import json
import os

import boto3
import pytest
import urllib.request

pytestmark = pytest.mark.integration

API_ENDPOINT = os.environ.get("API_ENDPOINT", "")
BUCKET_NAME = os.environ.get("S3_BUCKET", "")


@pytest.mark.skipif(not API_ENDPOINT, reason="API_ENDPOINT non défini — stack non déployé")
class TestLiveApi:
    def test_hello_endpoint(self):
        url = f"{API_ENDPOINT.rstrip('/')}/hello?name=IntegrationTest"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read())
        assert body["input_recu"] == "IntegrationTest"

    def test_s3_list_endpoint(self):
        url = f"{API_ENDPOINT.rstrip('/')}/s3/list?bucket={BUCKET_NAME}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            assert resp.status == 200


@pytest.mark.skipif(not BUCKET_NAME, reason="S3_BUCKET non défini — stack non déployé")
class TestLiveS3:
    def test_bucket_exists(self):
        s3 = boto3.client("s3")
        s3.head_bucket(Bucket=BUCKET_NAME)

    def test_bucket_versioning_enabled(self):
        s3 = boto3.client("s3")
        resp = s3.get_bucket_versioning(Bucket=BUCKET_NAME)
        assert resp.get("Status") == "Enabled"
