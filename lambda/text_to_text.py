import json
import openai
import unittest
import os
import boto3

secrets = boto3.client('secretsmanager')
open_ai_key_arn = os.environ.get('OPEN_AI_KEY_ARN')

def get_openai_api_key():
    print("Get stability api key")
    response = secrets.get_secret_value(
        SecretId=open_ai_key_arn,
    )
    api_key_json = json.loads(response['SecretString'])
    api_key = api_key_json['OPEN_AI_KEY']
    return api_key

def handler(event, context):
    print(event)

    # Check the event object before processing
    if event and ('body' in event) and 'prompt' in json.loads(event['body']):
        # Set the API key
        openai.api_key = get_openai_api_key()

        # Define the mock data
        prompt = json.loads(event['body'])['prompt']

        # Call the GPT-3 API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
        )
        if 'choices' in response and response['choices']:
            # Return the generated text
            return {
                'statusCode': 200,
                'body': json.dumps({'response': response['choices'][0]['text']})
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Error generating response'})
            }
    else:
        return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid request'})
        }

class TestGPT3APIHandler(unittest.TestCase):
    def test_valid_prompt(self):
        event = {'body': json.dumps({'prompt': 'What is the meaning of life?'})}
        response = handler(event, None)
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('response', json.loads(response['body']))
        
    def test_missing_prompt(self):
        event = {'body': json.dumps({})}
        response = handler(event, None)
        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body'])['error'], 'Invalid request')
        
    def test_error_response(self):
        # Set the api_key to an invalid key to force an error response
        openai.api_key = "invalid_key"
        event = {'body': json.dumps({'prompt': 'What is the meaning of life?'})}
        response = handler(event, None)
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])['error'], 'Error generating response')
