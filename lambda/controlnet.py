import boto3
import os
from io import BytesIO
import json
from PIL import Image
import requests
import base64
import time

CONTROL_NET_URL = 'https://stablediffusionapi.com/api/v5/controlnet'
secrets = boto3.client('secretsmanager')
sd_key_arn = os.environ.get('SD_API_KEY_ARN')

def get_sd_api_key():
    print("Get stable diffusion api key")
    response = secrets.get_secret_value(
        SecretId=sd_key_arn,
    )
    api_key_json = json.loads(response['SecretString'])
    api_key = api_key_json['SD_API_KEY']
    return api_key

def get_base64_string(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return img_str

def fetch_api(fetch_url, eta):
    print("Fetching from {}".format(fetch_url))

    response = requests.post(fetch_url, {
        "key": get_sd_api_key()
    })
    res_json = response.json()
    status = res_json.get('status', None)
    print(res_json)
    if status == 'success':
        return res_json
    else:
        print("Waiting for {} seconds".format(eta))
        time.sleep(int(eta))
        return fetch_api(fetch_url, eta)

def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # For testing
    # body = event["body"]
    body = json.loads(event["body"])

    # Get params
    prompt = body['prompt'] 
    init_image = body['image']
    width = int(body.get('width', 512))
    height = int(body.get('height', 512))
    model_id = body.get('modelId', "sd-1.5")
    controlnet_model = body.get('controlnetModel', "scribble")

    advanced_options = body['advancedOptions']

    samples = advanced_options.get('samples', "1")
    num_inference_steps = advanced_options.get('numInferenceSteps', "30")
    guidance_scale = advanced_options.get('guidanceScale', 7.5)
    strength = advanced_options.get('strength', 0.7)
    negative_prompt = advanced_options.get('negativePrompt', None)
    seed = advanced_options.get('seed', None)
    safety_checker = advanced_options.get('safetyChecker', "no")
    enhance_prompt = advanced_options.get('enhancePrompt', "yes")
    scheduler = advanced_options.get('scheduler', "UniPCMultistepScheduler")
    autohint = advanced_options.get('autohint', "yes")

    request = {
        "key": get_sd_api_key(),
        "model_id": model_id,
        "controlnet_model": controlnet_model,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "init_image": init_image,
        "width": width,
        "height": height,
        "samples": samples,
        "num_inference_steps": num_inference_steps,
        "safety_checker": safety_checker,
        "enhance_prompt": enhance_prompt,
        "scheduler": scheduler,
        "guidance_scale": guidance_scale,
        "strength": strength,
        "seed": seed,
        "auto_hint" : autohint,
        "webhook": None,
        "track_id": None
    }

    res = requests.post(CONTROL_NET_URL, json = request)
    res_json = res.json()
    status = res_json.get("status")

    print(res_json)

    # If status is processing, call api on fetch link
    if status == "processing":
        fetch_url = res_json.get("fetch_result")
        eta = res_json.get("eta", 5)
        res_json = fetch_api(fetch_url, eta)

    print(res_json)
    image_url = res_json.get("output")[0]

    # Download image and convert to base64
    res = requests.get(image_url)
    image = Image.open(BytesIO(res.content))
    image_base64 = get_base64_string(image)

    # Handle response
    response =  {
        "statusCode": 500,
        'headers': { 'Content-Type': 'application/json' },
        "body":  json.dumps({'error': "Unknown error"}),
    }
    if res.status_code == 200:
        response = {
            "statusCode": 200,
            'headers': { 'Content-Type': 'application/json' },
            "body": json.dumps({'image': image_base64}),
        }
     
    return response

if __name__ == '__main__':
    request = {
        "body": {
            "modelId": "icons-diffusion",
            "controlnetModel": "canny",
            "prompt": "3D pencil icon",
            "image": "https://aipencil-beta-image-bucket.s3.amazonaws.com/inputs/2023-03-12-23-50-17-ba7818a5-c037-4845-8204-2919d43457a2.png",
            "advancedOptions": {}
        }
    }
    response = handler(request, None)
    print(response)