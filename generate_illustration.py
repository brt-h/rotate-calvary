import openai
import requests
import os
# from dotenv import load_dotenv # is this being used?

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# openai.api_key = OPENAI_API_KEY # is this being used?

# This function calls the DALLE2 REST API
def generate_illustration(prompt, output_file):
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

        with open(output_file, "wb") as file:
            file.write(image_response.content)
    else:
        print(f"Error generating image: {response.status_code}, {response.text}")

generate_illustration("Magnificent wolf, ancient wisdom, fierce determination, fire spirit, forest background, warm lighting","image1.png")