# temporarily pull in example_output
# with open( './example_output.json', 'r') as read_file:
#     res = json.load(read_file)


import requests
import streamlit as st
import json
from PIL import Image
import base64
from io import BytesIO

# converts base64 string into an image
def base64_to_image(base64_string):
    img_data = base64.b64decode(base64_string)
    img = Image.open(BytesIO(img_data))
    return img

# defines an h1 header
st.title('Picturebook web app')

# displays a multi-line text input widget
des = st.text_area('Sentence/topic to use...', placeholder='''
    It was the best of times, it was the worst of times, it was
    the age of wisdom, it was the age of foolishness, it was
    the epoch of belief, it was the epoch of incredulity, it
    was the season of Light, it was the season of Darkness, it
    was the spring of hope, it was the winter of despair, (...)
    ''')

# displays a slider widget
pgs = st.slider('Number of pages...', 1, 5, 20)

# displays a button
if st.button('Generate'):
    if des is not None and pgs is not None:
        st.write('Generating...')

        # call backend
        response = requests.get(f"http://localhost:4000/get_storybook/?des={des}&pgs={pgs}")
        res = response.json()

        # not used
        # user_input = res['user_input']
        # total_pages = res['total_pages']

        title = res['title']
        st.write(f'Title: {title}')

        # Get the length of the parsed_text_description list
        n = len(res['parsed_text_description'])

        # Loop through to write each page
        for i in range(n):
            
            # assign
            page_text = res['parsed_text_description'][i]
            caption = res['parsed_image_description'][i]
            image = base64_to_image(res['illustrations'][i])

            # display
            st.write(f'Page {i+1}:  \n{page_text}')
            st.image(image, caption=caption)
