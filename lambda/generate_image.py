import boto3
import os
from io import BytesIO
import base64
import json
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image

secrets = boto3.client('secretsmanager')
stability_key_arn = os.environ.get('STABILITY_KEY_ARN')

def get_stability_api_key():
    print("Get stability api key")
    response = secrets.get_secret_value(
        SecretId=stability_key_arn,
    )
    api_key_json = json.loads(response['SecretString'])
    api_key = api_key_json['STABILITY_KEY']
    return api_key

def get_base64_string(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    body = json.loads(event["body"])

    # Get params
    prompt = body['prompt'] 
    width = int(body.get('width', 512))
    height = int(body.get('height', 512))

    # Advanced options
    advanced_options = body['advancedOptions']
    cfg_scale = advanced_options['cfgScale']
    seed = advanced_options['seed']
    sampler_index = advanced_options['samplerIndex']
    denoising_strength = advanced_options['denoisingStrength']

    init_img = None
    if body and 'image' in body:
        init_img = body['image']

    # Create client connection
    stability_api = client.StabilityInference(
        key=get_stability_api_key(), # API Key reference.
        verbose=True, # Print debug messages.
        engine="stable-diffusion-v1-5",  # Potentially use different engine for inpainting
    )

    # Call stability API
    if init_img: 
        # Image to image
        pil_init_image = Image.open(BytesIO(base64.b64decode(init_img)))
        # pil_init_image.thumbnail((512, 512))
        answers = stability_api.generate(
            prompt=prompt,
            init_image=pil_init_image,
            start_schedule=denoising_strength,
            seed=seed,
            steps=30,
            cfg_scale=cfg_scale,
            width=width,
            height=height,
            sampler=generation.SAMPLER_K_DPMPP_2M
        )
    else :
        # Text to image
        answers = stability_api.generate(
            prompt=prompt,
            seed=seed, 
            steps=30,
            cfg_scale=cfg_scale,
            width=width,
            height=height,
            samples=1,
            sampler=generation.SAMPLER_K_DPMPP_2M 
        )
    
    # Handle response
    response =  {
        "statusCode": 500,
        'headers': { 'Content-Type': 'application/json' },
        "body":  json.dumps({'error': "Unknown error"}),
    }
    for resp in answers:
        for artifact in resp.artifacts:
            # Check for content filters
            if artifact.finish_reason == generation.FILTER:
                error_message = "Your request activated the safety filters. Please change the prompt or drawing and try again."
                response = {
                    "statusCode": 500,
                    'headers': { 'Content-Type': 'application/json' },
                    "body": json.dumps({'error': error_message})
                }
                print(error_message)
                return response
            if artifact.type == generation.ARTIFACT_IMAGE:
                img = Image.open(BytesIO(artifact.binary))
                img_str = get_base64_string(img)
                response =  {
                    "headers": {
                        "Content-Type": "application/json"
                    },
                    "statusCode": 200,
                    "body": json.dumps({'image':img_str})
                }
                print("Image generated successfully") 
    return response

if __name__ == '__main__':
    request = {
        "body": {
            "prompt": "A nice green dog wearing a top hat"
        }
    }
    response = handler(json.dumps(request), None)
    print(response)