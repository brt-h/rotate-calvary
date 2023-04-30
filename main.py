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
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(OPENAI_API_KEY)
openai.api_key = OPENAI_API_KEY

# This is an LLMChain to create a title given a scentence/topic.
llm = OpenAI(temperature=.7)
template = """You are a creative picture book writer. Given a sentence/topic, it is your job to create a title suitable for a picture book.

Sentence/topic: {user_input}
Writer: This is a title for the above sentence/topic:"""
prompt_template = PromptTemplate(input_variables=["user_input"], template=template)
title_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="title")

# This is an LLMChain to write an synopsis of a picture book given a title and user input.
llm = OpenAI(temperature=.7)
template = """You are a creative picture book writer. Given the title of the 20 page picture book and the sentence/topic on which it's title is based, it is your job to write a synopsis for the picture book.

Title: {title}
Sentence/topic: {user_input}
Synopsis from a a creative picture book writer of the above picture book:"""
prompt_template = PromptTemplate(input_variables=["title","user_input"], template=template)
synopsis_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="synopsis")


# This is an LLMChain to write the text and image descriptions of a picture book given title and synopsis.
llm = OpenAI(temperature=.7)
template = """You are a creative picture book writer. Given the title and synopsis of the 20 page picture book, it is your job to write the text that should appear on each of the 20 pages as well as a description for the image to accompany the text on each page.

Title: {title}
Synopsis:
{synopsis}
Text and image description for each of the 20 pages from a creative picture book writer for the above picture book:"""
prompt_template = PromptTemplate(input_variables=["title","synopsis"], template=template)
text_and_image_description_chain = LLMChain(llm=llm, prompt=prompt_template, output_key="text_and_image_description")

# This is the overall chain where we run these three chains in sequence.
overall_chain = SequentialChain(
    chains=[title_chain, synopsis_chain, text_and_image_description_chain],
    input_variables=["user_input"],
    # Here we return multiple variables
    output_variables=["title", "synopsis","text_and_image_description"],
    verbose=True)

x = overall_chain({"user_input":"Martian fleet inspects rebel ship pretending to be freighter"})

print(x["title"])
print(x["synopsis"])
print(x["text_and_image_description"])











# fast api
# app = FastAPI()

# @app.get("/get_storybook/")
# async def get_storybook(users_book_description: str):
#     user_content_2 = PARTIAL_USER_CONTENT_2 + f"{users_book_description}\""
#     output = get_openai_response_combined(user_content_2)
#     return {"result": output}
