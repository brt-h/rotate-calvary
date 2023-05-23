# temporarily pull in example_output
# with open( './example_output.json', 'r') as read_file:
#     res = json.load(read_file)

import requests
import streamlit as st
import json
from PIL import Image
import base64
from io import BytesIO
import time
from sseclient import SSEClient

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
pgs = st.slider('Number of pages...', 1, 20, 5)

# displays a button
if st.button('Generate'):
    if des is not None and pgs is not None:
        st.write('Generating...')

        # Create a new task and get the task ID
        response = requests.get(f"http://localhost:4000/get_storybook/?des={des}&pgs={pgs}")
        print(response.text)
        task_id = response.json()["task_id"]
        
        # Connect to the update stream
        messages = SSEClient(f"http://localhost:4000/get_updates/{task_id}")

        # Process updates as they arrive
        for msg in messages:
            if msg.data:    # Checking if msg.data isn't empty
                try:
                    data = json.loads(msg.data)
                    print(data)
                except json.JSONDecodeError:
                    print(f'Invalid JSON: {msg.data}')
                    continue  # Skip this iteration and move to next message

                # Check if the task is done
                if data['status'] == 'done':
                    # Get the final output
                    final_output = data['final_output']

                    title = final_output['title']
                    st.write(f'Title: {title}')

                    # Get the length of the parsed_text_description list
                    n = len(final_output['parsed_text_description'])

                    # Loop through to write each page
                    for i in range(n):

                        # assign
                        page_text = final_output['parsed_text_description'][i]
                        caption = final_output['parsed_image_description'][i]
                        image = base64_to_image(final_output['illustrations'][i])

                        # display
                        st.write(f'Page {i+1}:  \n{page_text}')
                        st.image(image, caption=caption)

                    # Exit the loop when the task is done
                    break
                else:
                    # Update the frontend with the latest available data
                    if 'final_output' in data:
                        title = data['final_output']['title']
                        st.write(f'Title: {title}')

                        # Get the length of the parsed_text_description list
                        n = len(data['final_output']['parsed_text_description'])

                        # Loop through to write each page
                        for i in range(n):

                            # assign
                            page_text = data['final_output']['parsed_text_description'][i]
                            caption = data['final_output']['parsed_image_description'][i]
                            image = base64_to_image(data['final_output']['illustrations'][i])

                            # display
                            st.write(f'Page {i+1}:  \n{page_text}')
                            st.image(image, caption=caption)
