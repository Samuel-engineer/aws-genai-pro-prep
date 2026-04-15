import json
import os

import boto3
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver, Response
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError

logger = Logger()
app = APIGatewayHttpResolver()

MAX_LIST_KEYS = 20


def _get_s3_client():
    """Lazy S3 client — créé à l'appel, pas à l'import (nécessaire pour moto)."""
    return boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))


def _get_s3_bucket():
    """Lecture dynamique du bucket depuis l'env (nécessaire pour monkeypatch en tests)."""
    return os.environ.get("S3_BUCKET", "")


@app.get("/hello")
def hello():
    """Endpoint de bienvenue."""
    name = app.current_event.query_string_parameters.get("name", "Inconnu") if app.current_event.query_string_parameters else "Inconnu"
    logger.info(f"Hello endpoint called with name: {name}")
    return {
        "message": "Hello de la part d'AWS Lambda ! Prêt pour la GenAI.",
        "input_recu": name,
    }


@app.get("/s3/list")
def s3_list():
    """Liste les objets d'un bucket S3."""
    params = app.current_event.query_string_parameters or {}
    bucket = params.get("bucket") or _get_s3_bucket()
    prefix = params.get("prefix", "")

    if not bucket:
        logger.warning("S3 list called without bucket parameter")
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": "Paramètre 'bucket' manquant."}),
        )

    try:
        logger.info(f"Listing S3 bucket: {bucket} with prefix: {prefix}")
        s3 = _get_s3_client()
        resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=MAX_LIST_KEYS)
        keys = [obj["Key"] for obj in resp.get("Contents", [])]
        return {
            "bucket": bucket,
            "prefix": prefix,
            "objects": keys,
        }
    except ClientError as e:
        logger.exception(f"Error listing S3 bucket {bucket}")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )


@app.post("/s3/put")
def s3_put():
    """Écrit un objet texte dans S3."""
    try:
        body_data = app.current_event.json_body if app.current_event.body else {}
        bucket = body_data.get("bucket") or _get_s3_bucket()
        key = body_data.get("key")
        content = body_data.get("content", "")

        if not bucket or not key:
            logger.warning("S3 put called without bucket or key")
            return Response(
                status_code=400,
                content_type="application/json",
                body=json.dumps({"error": "Paramètres 'bucket' et 'key' requis."}),
            )

        logger.info(f"Writing to S3: s3://{bucket}/{key}")
        s3 = _get_s3_client()
        s3.put_object(Bucket=bucket, Key=key, Body=content.encode("utf-8"))
        return {
            "message": f"Objet '{key}' écrit dans '{bucket}'.",
        }
    except json.JSONDecodeError:
        logger.exception("Invalid JSON in request body")
        return Response(
            status_code=400,
            content_type="application/json",
            body=json.dumps({"error": "Body JSON invalide"}),
        )
    except ClientError as e:
        logger.exception("Error writing to S3")
        return Response(
            status_code=500,
            content_type="application/json",
            body=json.dumps({"error": str(e)}),
        )


@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """Entrypoint Lambda — dispatché par Powertools APIGatewayHttpResolver."""
    return app.resolve(event, context)