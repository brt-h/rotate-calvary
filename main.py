# TODO: improve response speed by breaking Python response object, add logic to create cohesive design language for all image prompts, add logic to check if length of list is equal to total pages, refactor to streaming output, make a title image with text rastered on top, refactor to chunk or stream or otherwise improve response time, image consistency efforts, pdf export (front end), save recently created stories (frontend, while waiting), fix the 'we solved lots of puzzles' writing style

# Some dependancies:
# !pip install python-dotenv
# !pip install fastapi
# !pip install openai
# !pip install uvicorn
# !pip install langchain

import time
import os
import openai
import json
import re
import base64
from generate_illustration import generate_illustration
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.llms import OpenAI # was used for old known good but expensive model
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback
from langchain.chains import OpenAIModerationChain
from io import BytesIO

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# llm = OpenAI(model_name="text-davinci-003",temperature=.7) # costs about ~$0.045 per run, seems to output a fraction of the pages asked for
# llm = ChatOpenAI(model_name="gpt-3.5-turbo",temperature=.7) # costs about ~$0.005 per run, seems prone to formatting errors
llm = ChatOpenAI(model_name="gpt-4", temperature=.7, request_timeout=240) # costs about ~$0.155 per run, seems higher quality, might be slowest

# This is an LLMChain to create a title given a scentence/topic.
template = """You are a creative picture book writer. Given a sentence/topic, it is your job to create a title suitable for a picture book.

Sentence/topic: {user_input}
Writer: This is a title for the above sentence/topic:"""
prompt_template = PromptTemplate(input_variables=["user_input"], template=template)
title_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="title")

# This is an LLMChain to write the text descriptions of a picture book given title and user_input.
template = """You are a creative picture book writer. Given the title and the provided sentence/topic of the {total_pages} page picture book, it is your job to write the text that should appear on each of the {total_pages} pages.

Title: {title}
Sentence/topic: {user_input}
Text for each of the {total_pages} pages from a creative picture book writer for the above picture book:"""
prompt_template = PromptTemplate(input_variables=["total_pages","title","user_input"], template=template)
text_description_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="text_description")

# This is an LLMChain to write the image descriptions of a picture book given title and user_input.
template = """You are an expert at creating input prompts for text-to-image neural networks. The system accepts as correct the query string, where all arguments are separated by commas.
The words in prompt are crucial. Users need to prompt what they want to see, specifying artist names, media sources, or art styles to get desired results. Be descriptive in a manne similar to prompts provided below about what you want. It is more sensitive to precise wording. That includes adjectives and prepositions like “in front of [x]“, and “taken by [camera name]“.
It also supports weights. By bracketing the words you can change their importance. For example, (rainy) would be twice as important compared to "rainy" for the model, and [rainy] would be half as important.

Write a medium lenth prompt, like below. Too long and it would fail to generate, too short and it would generate crap. Be as detailed as possible and avoid both scenarios at any cost.
As photographers and painters know, light has a huge effect on the final impression an image creates. Specify lighting conditions. Describe the type of light you want to see and the time of day it is. You don’t need complex vocabulary.

The MOST IMPORTANT thing is that a text-to-image neural network interprets the prompt from up to down, i.e. what is listed at the beginning of the prompt is more significant than what is listed near the end of the prompt. So it is recommended to place the subject of prompt in the beginning, characteristical tags in the middle and misc tags like lighting or camera settings near the end. Tags must be separated by commas, commas are not allowed in the query (what needs to be drawn), because the system treats it as one big tag.

Below few good examples are listed:
Example 1: Stunning wooden house, by James McDonald and Joarc Architects, home, interior, octane render, deviantart, cinematic, key art, hyperrealism, sun light, sunrays, canon eos c 300, ƒ 1.8, 35 mm, 8k, medium - format print
Example 2: Stunning concept art render of a mysterious magical forest with river passing through, epic concept art by barlowe wayne, ruan jia, light effect, volumetric light, 3d, ultra clear detailed, octane render, 8k, dark green, dark green and gray colour scheme
Example 3: Stunning render of a piece of steak with boiled potatoes, depth of field. bokeh. soft light. by Yasmin Albatoul, Harry Fayt. centered. extremely detailed. Nikon D850, (35mm|50mm|85mm). award winning photography.
Example 4: Stunning postapocalyptic rich marble building covered with green ivy, fog, animals, birds, deer, bunny, postapocalyptic, overgrown with plant life and ivy, artgerm, yoshitaka amano, gothic interior, 8k, octane render, unreal engine

Looking at the rules and examples listed above, and given the title and text for each page of a picture book, it is your job to create a prompt for the image that should accompany the text on each page.

Title: {title}
Text for each page:
{text_description}
Text-to-image neural network input prompts for each of the {total_pages} pages for the above picture book:"""
prompt_template = PromptTemplate(input_variables=["total_pages","title","text_description"], template=template)
image_description_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="image_description")

# This is the overall chain where we run these three chains in sequence.
overall_chain = SequentialChain(
    chains=[title_chain, text_description_chain, image_description_chain],
    input_variables=["total_pages","user_input"],
    output_variables=["title","text_description","image_description"],
    verbose=True)

# Set user input in prompt used through out
# user_input = "Fire spirit in the shape of a wolf guards the mountain from the humans who come to clear the forest"
# Set total number of pages in prompt used through out
# total_pages = 5

# parse text_description string to Python object 
def parse_text(input_text):
    pages = []
    page_pattern = re.compile(r"Page (\d+):(?:\n)?(.+?)(?=Page \d+:|$)", re.DOTALL)
    for match in page_pattern.finditer(input_text):
        pages.append(match.group(2).strip())
    return pages

#  convert images to serializable format. 
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue())
    return img_str.decode('utf-8')


def main(user_input,total_pages):
    # Main thread: moderation check, model usage information, call chain with user input, build final_output object
    
    # moderation check
    start_time = time.time()
    if OpenAIModerationChain(error=True).run(user_input):
        print("Vibe check passed.(moderation=True)")
        with get_openai_callback() as cb:
            x = overall_chain({"total_pages":total_pages,"user_input":user_input})
            print(f"Total Tokens: {cb.total_tokens}")
            print(f"Prompt Tokens: {cb.prompt_tokens}")
            print(f"Completion Tokens: {cb.completion_tokens}")
            print(f"Total Cost (USD): ${cb.total_cost}")
    else:
        print("Vibe check failed.(moderation=False)")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
    
    # print OpenAI API outputs
    # print("Title:",x["title"],sep='\n')
    # print("Text Description:",x["text_description"],sep='\n')
    # print("Image Description:",x["image_description"],sep='\n')
    
    # parse text description
    parsed_text_description = parse_text(x["text_description"])
    # print(parsed_text_description)
    
    # parse image description
    parsed_image_description = parse_text(x["image_description"])
    # print(parsed_image_description)
    illustrations = []
    for page in parsed_image_description:
        image = generate_illustration(page)
        # image.show()
        base64image = image_to_base64(image)
        illustrations.append(base64image)

    # build final_ouput object for API endpoint
    final_output = {}
    final_output['user_input'] = user_input # string
    final_output['total_pages'] = total_pages # int
    final_output['title'] = x["title"] # string
    final_output['parsed_text_description'] = parsed_text_description # list of strings
    final_output['parsed_image_description'] = parsed_image_description # list of strings
    final_output['illustrations'] = illustrations # list of strings (base64 encoded images)
    print(final_output)
    return final_output

app = FastAPI()
origins = [
    "http://localhost:3000",  # React app
    "http://localhost:8080",  # FastAPI server (change if different)
    "https://rotate-calvary.fly.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/get_storybook/")
async def get_storybook(des: str, pgs: int):
    user_input = des
    total_pages = pgs
    result = main(user_input,total_pages)
    return result

# if __name__ == "__main__":
#     start_time = time.time()
#     # fast api
#     @app.get("/get_storybook/")
#     async def get_storybook(des: str, pgs: int):
#         user_input = des
#         total_pages = pgs
#         final_output = main(user_input,total_pages)
#         return {"result": final_output}
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print(f"Execution time: {elapsed_time:.2f} seconds")