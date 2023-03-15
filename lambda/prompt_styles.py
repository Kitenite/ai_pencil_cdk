import boto3
import json
import os
from prompt_style_data import PromptStyleData

bucketName = os.environ.get('BUCKET_NAME')
s3 = boto3.resource('s3')

def handler(event, context):
    print(f"Returning prompt styles")
    promptStyleData = PromptStyleData()
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "promptStyles": promptStyleData.getPromptStyles(bucketName)
            }
        ),
    }
    
if __name__ == '__main__':
    response = handler(None, None)
    print(response)
