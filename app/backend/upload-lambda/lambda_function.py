import json 
import uuid
import boto3
import os


s3 = boto3.client("s3")
UPLOAD_BUCKET = os.environ["UPLOAD_BUCKET"]
ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp','image/jpg']
dynamodb = boto3.resource("dynamodb")
table_name = os.environ["DDB_TABLE"]
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    filename = body.get('filename')
    content_type = body.get('contentType')  

    

    if not content_type or not filename : 
        return response(400,{'error':'missing metadata'})

    content_type = content_type.lower()
    if content_type not in ALLOWED_TYPES:
        return response(400,{'error': 'file type not allowed'})

    image_id = str(uuid.uuid4())
    file_extension = filename.split(".")[-1]
    object_key = f'uploads/{image_id}.{file_extension}'

    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': UPLOAD_BUCKET,
                'Key': object_key,
                'ContentType': content_type
            },
            ExpiresIn=300 # 5 minutes
        )

        item={
            "Id": image_id ,
            "status" : "PENDING"
            }
        table.put_item(Item=item)

        return response(200,{'uploadUrl': presigned_url,'imageId': image_id})

    except Exception as e:
        print(f"lambda error : {str(e)}")

        return response(500,{'error': 'internal server error.'})


    
def response(status_code, body_dict):
    """standarized responses """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*' # add a domain later !!! yarbi mansach 
        },
        'body': json.dumps(body_dict)
    }