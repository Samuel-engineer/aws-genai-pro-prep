"""
Exercice S3 — Opérations de base avec boto3.

Ce script standalone permet de pratiquer les opérations S3
fondamentales en dehors de Lambda. Exécuter directement :

    cd scripts/
    python s3_operations.py --bucket MON-BUCKET --action list
    python s3_operations.py --bucket MON-BUCKET --action upload --key data/test.txt --file ./local.txt
    python s3_operations.py --bucket MON-BUCKET --action download --key data/test.txt --file ./output.txt
"""

import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError


def list_objects(s3, bucket, prefix=""):
    """Liste les objets d'un bucket avec pagination."""
    paginator = s3.get_paginator("list_objects_v2")
    count = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            print(f"  {obj['Key']:60s}  {obj['Size']:>10d} bytes  {obj['LastModified']}")
            count += 1
    print(f"\nTotal: {count} objet(s)")


def upload_file(s3, bucket, key, local_path):
    """Upload un fichier local vers S3."""
    s3.upload_file(local_path, bucket, key)
    print(f"Uploadé: {local_path} -> s3://{bucket}/{key}")


def download_file(s3, bucket, key, local_path):
    """Télécharge un objet S3 en local."""
    s3.download_file(bucket, key, local_path)
    print(f"Téléchargé: s3://{bucket}/{key} -> {local_path}")


def create_bucket(s3, bucket, region="us-east-1"):
    """Crée un bucket S3."""
    params = {"Bucket": bucket}
    if region != "us-east-1":
        params["CreateBucketConfiguration"] = {"LocationConstraint": region}
    s3.create_bucket(**params)
    print(f"Bucket créé: {bucket} (région: {region})")


def get_bucket_info(s3, bucket):
    """Affiche les infos du bucket (versioning, region)."""
    location = s3.get_bucket_location(Bucket=bucket)
    region = location["LocationConstraint"] or "us-east-1"

    try:
        versioning = s3.get_bucket_versioning(Bucket=bucket)
        ver_status = versioning.get("Status", "Désactivé")
    except ClientError:
        ver_status = "Inconnu"

    print(f"Bucket: {bucket}")
    print(f"  Région:     {region}")
    print(f"  Versioning: {ver_status}")


def main():
    parser = argparse.ArgumentParser(description="Exercice S3 — Opérations de base")
    parser.add_argument("--bucket", required=True, help="Nom du bucket S3")
    parser.add_argument("--action", required=True,
                        choices=["list", "upload", "download", "create-bucket", "info"],
                        help="Action à effectuer")
    parser.add_argument("--key", help="Clé S3 de l'objet")
    parser.add_argument("--file", help="Chemin du fichier local")
    parser.add_argument("--prefix", default="", help="Préfixe pour le listing")
    parser.add_argument("--region", default="us-east-1", help="Région AWS")
    args = parser.parse_args()

    s3 = boto3.client("s3", region_name=args.region)

    try:
        if args.action == "list":
            list_objects(s3, args.bucket, args.prefix)
        elif args.action == "upload":
            if not args.key or not args.file:
                sys.exit("--key et --file requis pour upload")
            upload_file(s3, args.bucket, args.key, args.file)
        elif args.action == "download":
            if not args.key or not args.file:
                sys.exit("--key et --file requis pour download")
            download_file(s3, args.bucket, args.key, args.file)
        elif args.action == "create-bucket":
            create_bucket(s3, args.bucket, args.region)
        elif args.action == "info":
            get_bucket_info(s3, args.bucket)
    except ClientError as e:
        print(f"Erreur AWS: {e.response['Error']['Message']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
