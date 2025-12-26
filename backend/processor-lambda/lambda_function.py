import boto3
import json
import os
from PIL import Image , ExifTags
import io

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["DDB_TABLE"]
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']  # uploads/<uuid>
    uuid= key.split("/")[1]

    # Get S3 object metadata
    obj = s3.get_object(Bucket=bucket, Key=key)
    size = obj["ContentLength"]
    content_type = obj["ContentType"]
    uploaded_at = obj["LastModified"].isoformat()
    filename= obj["Metadata"].get("filename")
    extension=filename.split(".")[-1]

    # Download object bytes for image inspection
    body_bytes = obj['Body'].read()

    # Try to extract image metadata using Pillow
    width = None
    height = None
    img_format = None
    mode = None
    exif = {}

    try:
        
        img = Image.open(io.BytesIO(body_bytes))
        width, height = img.size
        img_format = img.format
        mode = img.mode

        # Extract EXIF if available (may be None)
        try:
            raw_exif = img._getexif() or {}
            exif = {ExifTags.TAGS.get(k, str(k)): str(v) for k, v in raw_exif.items()}
        except Exception as ex:
            print('EXIF extraction failed:', ex)
    except Exception as e:
        print('Pillow not installed or failed to process image:', e)

    item = {
        "Id": uuid,
        "filename": filename,
        "extension": extension,
        "size": size,
        "contentType": content_type,
        "uploadTime": uploaded_at,
        "s3Key": key,
        "width": width,
        "height": height,
        "format": img_format,
        "mode": mode,
        "EXIF": exif
    }

    print("Writing item:", item)

    try:
        table.put_item(Item=item)
    except Exception as e:
        print("DynamoDB error:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    return {"statusCode": 200, "body": "OK"}
