import json 
import base64
import uuid
import boto3
import requests_toolbelt.multipart.decoder as decoder
import os
UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]
s3 = boto3.client("s3")

def lambda_handler(event, context):

    body = base64.b64decode(event['body'])
    content_type = event['headers'].get("Content-Type") or event['headers'].get("content-type")

    MultiParts = decoder.MultipartDecoder(body, content_type)
    file = None
    file_name = None
    file_content_type = None

    for part in MultiParts.parts:
        cd = part.headers.get(b"Content-Disposition").decode()

        if 'filename=' in cd:
            file_name = cd.split('filename=')[1].strip('"')
            file = part.content
            file_content_type = part.headers.get(b"Content-Type", b"application/octet-stream").decode()

    if file is None or file_name is None:
        return {
            'statusCode': 400,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({'message': 'No file found in the request'})
        }

    id = str(uuid.uuid4())
    object_key = f'uploads/{id}'

    try:
        s3.put_object(
            Bucket=UPLOAD_BUCKET,
            Key=object_key,
            Body=file,
            ContentType=file_content_type,
            Metadata={"filename": file_name}
        )

        # Return Id (capitalized) to match DynamoDB / other lambdas and include CORS
        return {
            'statusCode': 200,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({
                "Id": id,
                "message": "File uploaded successfully"
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            'body': json.dumps({'message': 'Error uploading file', 'error': str(e)})
        }
