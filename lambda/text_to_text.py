import json
import openai
import unittest
import os
import boto3

secrets = boto3.client('secretsmanager')
open_ai_key_arn = os.environ.get('OPEN_AI_KEY_ARN')
prompt_helper = ""
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
        
        prompt = prompt + prompt_helper

        # Call the GPT-3 API
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
        )
        if 'choices' in response and response['choices']:
            # Return the generated text
            res_text = response['choices'][0]['text']
            pos_prompt = res_text.strip(" ").strip("\n")
            # neg_prompt = res_text[1].strip("Negative Prompt:")
            return {
                'statusCode': 200,
                'body': json.dumps({'positive': pos_prompt, 'negative': ''})
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


prompt_helper ="""
use this information to learn about Stable diffusion Prompting, and use it to create prompts.
Stable Diffusion is an AI art generation model similar to DALLE-2. 
It can be used to create impressive artwork by using prompts. Prompts describe what should be included in the image. 
very important is that the Prompts are usually created in a specific structure: 
(Subject), (Action), (Context), (Environment), (Lightning),  (Artist), (Style), (Medium), (Type), (Color Scheme), (Computer graphics), (Quality), (etc.)
Subject: Person, animal, landscape
Action: dancing, sitting, surveil
Verb: What the subject is doing, such as standing, sitting, eating, dancing, surveil
Adjectives: Beautiful, realistic, big, colorful
Context: Alien planet's pond, lots of details
Environment/Context: Outdoor, underwater, in the sky, at night
Lighting: Soft, ambient, neon, foggy, Misty
Emotions: Cosy, energetic, romantic, grim, loneliness, fear
Artist: Pablo Picasso, Van Gogh, Da Vinci, Hokusai 
Art medium: Oil on canvas, watercolor, sketch, photography
style: Polaroid, long exposure, monochrome, GoPro, fisheye, bokeh, Photo, 8k uhd, dslr, soft lighting, high quality, film grain, Fujifilm XT3
Art style: Manga, fantasy, minimalism, abstract, graffiti
Material: Fabric, wood, clay, Realistic, illustration, drawing, digital painting, photoshop, 3D
Color scheme: Pastel, vibrant, dynamic lighting, Green, orange, red
Computer graphics: 3D, octane, cycles
Illustrations: Isometric, pixar, scientific, comic
Quality: High definition, 4K, 8K, 64K
example Prompts:
- overwhelmingly beautiful eagle framed with vector flowers, long shiny wavy flowing hair, polished, ultra detailed vector floral illustration mixed with hyper realism, muted pastel colors, vector floral details in background, muted colors, hyper detailed ultra intricate overwhelming realism in detailed complex scene with magical fantasy atmosphere, no signature, no watermark
- electronic robot and office ,unreal engine, cozy indoor lighting, artstation, detailed, digital painting, cinematic,character design by mark ryden and pixar and hayao miyazaki, unreal 5, daz, hyperrealistic, octane render
- underwater world, plants, flowers, shells, creatures, high detail, sharp focus, 4k
- picture of dimly lit living room, minimalist furniture, vaulted ceiling, huge room, floor to ceiling window with an ocean view, nighttime
- A beautiful painting of water spilling out of a broken pot, earth colored clay pot, vibrant background, by greg rutkowski and thomas kinkade, Trending on artstation, 8k, hyperrealistic, extremely detailed
- luxus supercar in drive way of luxus villa in black dark modern house with sunlight black an white modern
- highly detailed, majestic royal tall ship on a calm sea, realistic painting, by Charles Gregory Artstation and Antonio Jacobsen and Edward Moran, (long shot), clear blue sky, intricate details, 4k
- smooth meat table, restaurant, paris, elegant, lights

Very important: use an artist matching to the art style , or don't write any artist if it is realistic style or some of that.

I want you to write me one full detailed prompt about the idea written from me. Limit to 350 characters.
"""
