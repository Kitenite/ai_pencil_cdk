import os
import boto3
import json
from datetime import datetime
import uuid
import base64

bucket_name = os.environ.get('BUCKET_NAME')
s3 = boto3.resource('s3')
input_bucket_folder = "inputs"

def uploadImageToS3(input_location, img_data):
    print(f"Uploading image to S3 location {input_location}")
    s3object = s3.Object(bucket_name, input_location)
    s3object.put(Body=base64.b64decode(img_data), Key=input_location)
    # Get object url
    object_url = f"https://{bucket_name}.s3.amazonaws.com/{input_location}"
    object_acl = s3.ObjectAcl(bucket_name, input_location)
    response = object_acl.put(ACL='public-read')
    print(response)
    return object_url

def handler(event, context):
    body = json.loads(event["body"])

    # Get params
    init_img = body['image']

    input_file_name = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid.uuid4()}.png"
    s3_input_location = f"{input_bucket_folder}/{input_file_name}"
    # s3_img_url = f"s3://{bucket_name}/{input_bucket_folder}/{input_file_name}"
    download_url = uploadImageToS3(s3_input_location, init_img)

    # Send response
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body":  json.dumps({'img_url': download_url}),
    }

    return response