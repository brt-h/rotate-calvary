# Some dependancies:
# !pip install python-dotenv
# !pip install fastapi
# !pip install openai
# !pip install uvicorn
# !pip install langchain

import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI
import openai # gpt-3.5-turbo-0301
import re
from langchain.llms import OpenAI # was used for old known good but expensive model
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback
from langchain.chains import OpenAIModerationChain


OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# llm = OpenAI(temperature=.7) # old known good but expensive model
llm = ChatOpenAI(model="gpt-3.5-turbo",temperature=.7)

# This is an LLMChain to create a title given a scentence/topic.
template = """You are a creative picture book writer. Given a sentence/topic, it is your job to create a title suitable for a picture book.

Sentence/topic: {user_input}
Writer: This is a title for the above sentence/topic:"""
prompt_template = PromptTemplate(input_variables=["user_input"], template=template)
title_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="title")

# This is an LLMChain to write an synopsis of a picture book given a title and user input.
template = """You are a creative picture book writer. Given the title of the 20 page picture book and the sentence/topic on which it's title is based, it is your job to write a synopsis for the picture book.

Title: {title}
Sentence/topic: {user_input}
Synopsis from a a creative picture book writer of the above picture book:"""
prompt_template = PromptTemplate(input_variables=["title","user_input"], template=template)
synopsis_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="synopsis")


# This is an LLMChain to write the text descriptions of a picture book given title and synopsis.
template = """You are a creative picture book writer. Given the title and synopsis of the 20 page picture book, it is your job to write the text that should appear on each of the 20 pages.

Title: {title}
Synopsis:
{synopsis}
Text for each of the 20 pages from a creative picture book writer for the above picture book:"""
prompt_template = PromptTemplate(input_variables=["title","synopsis"], template=template)
text_description_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="text_description")

# This is an LLMChain to write the image descriptions of a picture book given title and synopsis.
template = """You are an expert at creating input prompts for text-to-image neural networks. The system acepts as correct the query string,where all arguments are separated by commas. The words in prompt are crucial. Users need to prompt what they want to see, specifying artist names, media sources, or art styles to get desired results. It is more sensitive to precise wording. That includes adjectives and prepositions like “in front of [x]“, and “taken by [camera name]“. It also supports weights. By bracketing the words you can change their importance. For example, (rainy) would be twice as important compared to "rainy" for the model, and [rainy] would be half as important. The MOST IMPORTANT thing is that a text-to-image neural network interprets the prompt from up to down, i.e. what is listed at the beginning of the prompt is more significant than what is listed near the end of the prompt. So it is recommended to place the subject of prompt in the beginning, characteristical tags in the middle and misc tags like lighting or camera settings near the end. Tags must be separated by commas, commas are not allowed in the query (what needs to be drawn), because the system treats it as one big tag. Given the title and text for each page, it is your job to write the prompt for the image that should accompany the text on each page.

Title: {title}
Text for each page:
{text_description}
Text-to-image neural network input prompts for each of the 20 pages for the above picture book:"""
prompt_template = PromptTemplate(input_variables=["title","text_description"], template=template)
image_description_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="image_description")

# This is the overall chain where we run these three chains in sequence.
with get_openai_callback() as cb:
    overall_chain = SequentialChain(
        chains=[title_chain, synopsis_chain, text_description_chain, image_description_chain],
        input_variables=["user_input"],
        output_variables=["title","synopsis","text_description","image_description"],
        verbose=True)
    print(f"Total Tokens: {cb.total_tokens}")
    print(f"Prompt Tokens: {cb.prompt_tokens}")
    print(f"Completion Tokens: {cb.completion_tokens}")
    print(f"Total Cost (USD): ${cb.total_cost}")

# User input
# user_input = "Martian fleet inspects rebel ship pretending to be freighter"
user_input = "I will kill you"

# Moderation check
if OpenAIModerationChain(error=True).run(user_input):
    print("Vibe check passed.(moderation=True)")
    x = overall_chain({"user_input":user_input})
else:
    print("Vibe check failed.(moderation=False)")

print("Title:",x["title"])
print("Synopsis:",x["synopsis"])
print("Text Description:",x["text_description"])
print("Image Description:",x["image_description"])











# fast api
# app = FastAPI()

# @app.get("/get_storybook/")
# async def get_storybook(users_book_description: str):
#     user_content_2 = PARTIAL_USER_CONTENT_2 + f"{users_book_description}\""
#     output = get_openai_response_combined(user_content_2)
#     return {"result": output}
