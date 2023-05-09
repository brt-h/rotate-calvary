import openai
import requests
import os
from PIL import Image
from io import BytesIO

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# This function calls the DALLE2 REST API
def generate_illustration(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }

    response = requests.post("https://api.openai.com/v1/images/generations", json=data, headers=headers)

    if response.status_code == 200:
        image_url = response.json()["data"][0]["url"]
        image_response = requests.get(image_url)
        
        # Load the image using PIL.Image and BytesIO
        image = Image.open(BytesIO(image_response.content))
        return image
    else:
        print(f"Error generating image: {response.status_code}, {response.text}")
        return None