import os
import json
import uuid
import datetime
import base64
import boto3
import csv
from io import StringIO

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")

UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]          # 既存
PRODUCT_TABLE = os.environ["PRODUCT_TABLE_NAME"]     # ← 新しく追加

def lambda_handler(event, context):
    try:
        print("=== Raw event ===")
        print(json.dumps(event)[:500])

        # --------------- CSV テキスト取得 ---------------
        body = event.get("body", "")
        if event.get("isBase64Encoded"):
            csv_text = base64.b64decode(body).decode("utf-8")
        else:
            csv_text = body

        print("=== CSV content ===")
        print(csv_text)

        # --------------- CSV をパース ---------------
        f = StringIO(csv_text)
        reader = csv.DictReader(f)  # 1行目のヘッダをキーとして使う

        items = []
        for row in reader:
            # 想定ヘッダ:
            # store_id,product_id,product_name,price,image_key
            print("Row:", row)

            item = {
                "store_id":     {"S": str(row["store_id"])},
                "product_id":   {"S": str(row["product_id"])},
                "product_name": {"S": row["product_name"]},
                "price":        {"N": str(row["price"])},
                "image_key":    {"S": row["image_key"]},
            }

            items.append({"PutRequest": {"Item": item}})

        # --------------- DynamoDB BatchWrite (25件ずつ) ---------------
        def batch_write(batch_items):
            if not batch_items:
                return
            resp = dynamodb.batch_write_item(
                RequestItems={PRODUCT_TABLE: batch_items}
            )
            if resp.get("UnprocessedItems"):
                print("UnprocessedItems:", resp["UnprocessedItems"])

        batch = []
        for it in items:
            batch.append(it)
            if len(batch) == 25:
                print("Writing 25 items to DynamoDB...")
                batch_write(batch)
                batch = []

        if batch:
            print(f"Writing last {len(batch)} items to DynamoDB...")
            batch_write(batch)

        # --------------- CSV 自体もS3に保存しておく（履歴用） ---------------
        key = "uploads/{}_{}.csv".format(
            datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            uuid.uuid4().hex[:8]
        )

        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=key,
            Body=csv_text,
            ContentType="text/csv",
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "message": "uploaded and inserted products",
                "csv_key": key,
                "item_count": len(items),
            })
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
