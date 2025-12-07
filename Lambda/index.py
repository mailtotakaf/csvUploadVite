import os
import json
import uuid
import datetime
import base64
import boto3

s3 = boto3.client("s3")
UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]

def lambda_handler(event, context):
    try:
        print("=== Raw event ===")
        print(json.dumps(event)[:500])

        body = event.get("body", "")

        # Base64 のときはデコード
        if event.get("isBase64Encoded"):
            csv_text = base64.b64decode(body).decode("utf-8")
        else:
            csv_text = body

        print("=== CSV content ===")
        print(csv_text)

        # S3 保存処理（あなたのコードそのまま）
        key = "uploads/{}_{}.csv".format(
            datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            uuid.uuid4().hex[:8]
        )

        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=key,
            Body=csv_text,
            ContentType="text/csv"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"message": "uploaded", "key": key})
        }

    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": str(e)})
        }
import os
import json
import uuid
import datetime
import base64
import boto3

s3 = boto3.client("s3")
UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]

def lambda_handler(event, context):
    try:
        print("=== Raw event ===")
        print(json.dumps(event)[:500])

        body = event.get("body", "")

        # Base64 のときはデコード
        if event.get("isBase64Encoded"):
            csv_text = base64.b64decode(body).decode("utf-8")
        else:
            csv_text = body

        print("=== CSV content ===")
        print(csv_text)

        # S3 保存処理（あなたのコードそのまま）
        key = "uploads/{}_{}.csv".format(
            datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            uuid.uuid4().hex[:8]
        )

        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=key,
            Body=csv_text,
            ContentType="text/csv"
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"message": "uploaded", "key": key})
        }

    except Exception as e:
        print("Error:", e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": str(e)})
        }
