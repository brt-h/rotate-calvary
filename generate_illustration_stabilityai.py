import os
import requests
import boto3
import uuid
from io import BytesIO
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

load_dotenv()

def generate_illustration(prompt):
    # Set your variables
    # engine_id = "stable-diffusion-v1-5"
    engine_id = "stable-diffusion-xl-beta-v2-2-2"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = os.getenv("STABILITYAI_API_KEY")
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # Check for missing parameters
    if api_key is None:
        raise Exception("Missing Stability API key.")
    if s3_bucket is None:
        raise Exception("Missing S3 bucket name.")
    if aws_access_key_id is None or aws_secret_access_key is None:
        raise Exception("Missing AWS credentials.")
    
    # Call the Stability.ai Stable Diffusion REST API
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "image/png",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": prompt
                }
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 512,
            "width": 512,
            "samples": 1,
            "steps": 30,
            "style_preset": "comic-book",
        },
    )
    
    # Handle unsuccessful responses
    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    image_data = response.content
    
    # Generate a unique image filename
    image_file_name = f"txt2img_{uuid.uuid4()}.png"

    # Initialize S3 client and upload file
    s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    try:
        with BytesIO(image_data) as data:
            s3_client.upload_fileobj(data, s3_bucket, image_file_name)
            print(f'Successfully uploaded {image_file_name} to {s3_bucket}')
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")

    # Generate the URL to get the uploaded image
    url = f"https://{s3_bucket}.s3.amazonaws.com/{image_file_name}"
    
    return url
