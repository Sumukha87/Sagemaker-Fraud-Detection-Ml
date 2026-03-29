"""
verify_setup.py — Checks that LocalStack and MLflow are alive and usable.

Run: python scripts/verify_setup.py
"""

import sys

import boto3
import mlflow
import requests

LOCALSTACK_URL = "http://localhost:4566"
MLFLOW_URL = "http://localhost:5000"


def check_localstack():
    print("Checking LocalStack...", end=" ")
    try:
        resp = requests.get(f"{LOCALSTACK_URL}/_localstack/health", timeout=3)
        data = resp.json()
        services = data.get("services", {})
        running = [k for k, v in services.items() if v in ("running", "available")]
        print(f"OK — {len(running)} services up: {', '.join(running[:5])}{'...' if len(running) > 5 else ''}")
        return True
    except Exception as e:
        print(f"FAIL — {e}")
        print("  → Is Docker running? Try: docker compose up -d")
        return False


def check_s3():
    print("Checking S3 via boto3...", end=" ")
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=LOCALSTACK_URL,
            region_name="us-east-1",
            aws_access_key_id="fake",
            aws_secret_access_key="fake",
        )
        s3.list_buckets()
        print("OK — boto3 can talk to LocalStack S3")
        return True
    except Exception as e:
        print(f"FAIL — {e}")
        return False


def check_mlflow():
    print("Checking MLflow...", end=" ")
    try:
        mlflow.set_tracking_uri(MLFLOW_URL)
        client = mlflow.tracking.MlflowClient()
        client.search_experiments()
        print(f"OK — MLflow tracking server at {MLFLOW_URL}")
        return True
    except Exception as e:
        print(f"FAIL — {e}")
        print("  → Is Docker running? Try: docker compose up -d")
        return False


def main():
    print("=" * 50)
    print("LocalSage Setup Verification")
    print("=" * 50)

    results = [
        check_localstack(),
        check_s3(),
        check_mlflow(),
    ]

    print("=" * 50)
    if all(results):
        print("All checks passed. Ready to run the pipeline.")
        sys.exit(0)
    else:
        failed = results.count(False)
        print(f"{failed} check(s) failed. Fix the issues above before running scripts.")
        sys.exit(1)


if __name__ == "__main__":
    main()
