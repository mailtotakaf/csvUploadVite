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

UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]
PRODUCT_TABLE = os.environ["PRODUCT_TABLE_NAME"]  # CFn の Environment で設定済み想定


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    }


def lambda_handler(event, context):
    print("=== Raw event ===")
    print(json.dumps(event)[:500])

    http_method = event.get("httpMethod")
    path = event.get("path", "")

    # CORS プリフライト
    if http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": ""
        }

    # POST /upload → CSV受付 & DynamoDB登録 & S3保存
    if http_method == "POST" and path.endswith("/upload"):
        return handle_post_upload(event)

    # GET /products?store_id=xxx → 商品一覧取得
    if http_method == "GET" and path.endswith("/products"):
        return handle_get_products(event)

    # それ以外
    return {
        "statusCode": 404,
        "headers": cors_headers(),
        "body": json.dumps({"error": "Not found"})
    }


# =======================
# POST /upload 用
# =======================

def handle_post_upload(event):
    try:
        csv_text = get_csv_text_from_event(event)
        items = parse_csv_to_items(csv_text)
        write_products_to_ddb(items)
        key = save_csv_to_s3(csv_text)

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({
                "message": "uploaded and inserted products",
                "csv_key": key,
                "item_count": len(items),
            })
        }

    except Exception as e:
        print("Error in handle_post_upload:", e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }


def get_csv_text_from_event(event):
    body = event.get("body", "")
    if event.get("isBase64Encoded"):
        return base64.b64decode(body).decode("utf-8")
    else:
        return body


def parse_csv_to_items(csv_text):
    """
    想定CSV:
    store_id,product_id,product_name,price,image_key
    101,P001,おにぎり鮭,130,product-images/101/P001.jpg
    ...
    """
    f = StringIO(csv_text)
    reader = csv.DictReader(f)

    items = []
    for row in reader:
        print("Row:", row)
        item = {
            "store_id":     {"S": str(row["store_id"])},
            "product_id":   {"S": str(row["product_id"])},
            "product_name": {"S": row["product_name"]},
            "price":        {"N": str(row["price"])},
            "image_key":    {"S": row["image_key"]},
        }
        items.append({"PutRequest": {"Item": item}})
    return items


def write_products_to_ddb(items):
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


def save_csv_to_s3(csv_text):
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
    return key


# =======================
# GET /products 用
# =======================

def handle_get_products(event):
    try:
        qs = event.get("queryStringParameters") or {}
        store_id = qs.get("store_id")
        if not store_id:
            return {
                "statusCode": 400,
                "headers": cors_headers(),
                "body": json.dumps({"error": "store_id is required"})
            }

        resp = dynamodb.query(
            TableName=PRODUCT_TABLE,
            KeyConditionExpression="store_id = :sid",
            ExpressionAttributeValues={
                ":sid": {"S": store_id}
            }
        )

        items = [
            {
                "store_id": i["store_id"]["S"],
                "product_id": i["product_id"]["S"],
                "product_name": i["product_name"]["S"],
                "price": int(i["price"]["N"]),
                "image_key": i["image_key"]["S"],
            }
            for i in resp.get("Items", [])
        ]

        return {
            "statusCode": 200,
            "headers": cors_headers(),
            "body": json.dumps({"items": items})
        }

    except Exception as e:
        print("Error in handle_get_products:", e)
        return {
            "statusCode": 500,
            "headers": cors_headers(),
            "body": json.dumps({"error": str(e)})
        }
