import boto3
from io import BytesIO
import json
import base64
import replicate
import os

secrets = boto3.client('secretsmanager')
replicate_key_arn = os.environ.get('REPLICATE_KEY_ARN')

def set_replicate_api_key():
    print("Get stability api key")
    response = secrets.get_secret_value(
        SecretId=replicate_key_arn,
    )
    api_key_json = json.loads(response['SecretString'])
    api_key = api_key_json['REPLICATE_API_TOKEN']
    os.environ["REPLICATE_API_TOKEN"] = api_key

#  Requires setting REPLICATE_API_TOKEN environment variable
def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Set up replicate
    set_replicate_api_key()
    # TODO: Other controlnet models

    # For testing
    # body = event["body"]
    # For production
    body = json.loads(event["body"])

    # Get params
    prompt = body['prompt'] 
    base64_img = body['image']

    # Get Buffered reader from base64 string
    buffered_img = BytesIO(base64.b64decode(base64_img))

    advanced_options = body.get('advancedOptions', {})

    model_type = advanced_options.get('modelType', "scribble")
    samples = advanced_options.get('samples', "1")
    guidance_scale = advanced_options.get('guidanceScale', 7.5)
    negative_prompt = advanced_options.get('negativePrompt', "longbody, lowres, bad anatomy, bad hands, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality")
    added_prompt = advanced_options.get('addedPrompt', "best quality, extremely detailed")
    ddim_steps = advanced_options.get('ddimSteps', 20)
    
    seed = advanced_options.get('seed', None)

    if model_type == "scribble":
        # More optimized verison of controlnet scribble
        model = replicate.models.get("jagilley/controlnet-scribble")
        version = model.versions.get("435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117")
    else:
        model = replicate.models.get("jagilley/controlnet")
        version = model.versions.get("8ebda4c70b3ea2a2bf86e44595afb562a2cdf85525c620f1671a78113c9f325b")

    # https://replicate.com/jagilley/controlnet-scribble/versions/435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117#input
    inputs = {
        'image': buffered_img,
        'prompt': prompt,
        'model_type': model_type, # canny, depth, hed, normal, mlsd, scribble, seg, openpose
        'num_samples': samples,
        'image_resolution': "512", # 256, 512, 768
        'detect_resolution': "512", # 256, 512, 768
        'ddim_steps': ddim_steps,
        'scale': guidance_scale, # 0.1 to 30
        'seed': seed,
        'eta': 0,
        'a_prompt': added_prompt,
        'n_prompt': negative_prompt
    }
    print(f"Input: {inputs}")

    # https://replicate.com/jagilley/controlnet-scribble/versions/435061a1b5a4c1e26740464bf786efdfa9cb3a3ac488595a2de23e143fdb0117#output-schema
    try: 
        output = version.predict(**inputs)
        print(f"Output: {output}")
        input_img_url = output[0]
        output_img_url = output[1]
        return {
            "statusCode": 200,
            'headers': { 'Content-Type': 'application/json' },
            "body": json.dumps({'image': output_img_url}),
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            'headers': { 'Content-Type': 'application/json' },
            "body":  json.dumps({'error': str(e)}),
        }
    

if __name__ == '__main__':
    request = {
        "body": {
            "prompt": "Bird",
            "modelType": "scribble",
            "image": "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",
            "advancedOptions": {}
        }
    }
    response = handler(request, None)
    print(response)