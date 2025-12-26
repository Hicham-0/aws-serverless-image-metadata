import boto3
import json
import os
from decimal import Decimal

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float(v) for v in obj]
    return obj



dynamodb=boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('DDB_TABLE')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event,context):
    #/result/{id}
    image_id=event.get("pathParameters", {}).get("id")
     
     
    #fetch the item for dynamodb 
    response=table.get_item(Key={"Id":image_id})
    if "Item" not in response:
           
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": "Metadata not found"})
        }

    item=response["Item"]
    
    data={
        "Id":item["Id"],
        "filename": item.get("filename"),
        "extension": item.get("extension"),
        "size": item.get("size"),
        "contentType": item.get("contentType"),
        "uploadTime": item.get("uploadTime"),
        "width": item.get("width"),
        "height": item.get("height"),
        "mode": item.get("mode"),
        "format": item.get("format"),
        "s3Key": item.get("s3Key"),
        "exif": item.get("EXIF", {})   
    }
    
    
    return{
        
        "statusCode":200,
        "headers":{"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps(data, default=decimal_to_float)
    }
    
    