import requests
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

# removes data: prefix from msg.data
def parse_sse_data(sse_line):
    prefix = "data: "
    if sse_line.startswith(prefix):
        json_line = sse_line[len(prefix):]
        return json.loads(json_line)
    else:
        print(msg.data)
        raise ValueError("Invalid SSE line")
# sse_line = 'data: {"status": "working", "progress": {"total": 4, "current": 0}, "data": null}'
# data = parse_sse_data(sse_line)
# print(data)

# defines an h1 header
print('Picturebook web app')

# displays a multi-line text input widget
des = "Super salty tomato soup"

# displays a slider widget
pgs = 3

# displays a button
# if st.button('Generate'):
if des is not None and pgs is not None:
    print('Generating...')

    # Create a new task and get the task ID
    response = requests.get(f"http://localhost:4000/get_storybook/?des={des}&pgs={pgs}")
    print(response.text)
    task_id = response.json()["task_id"]
    
    # Connect to the update stream
    messages = SSEClient(f"http://localhost:4000/get_updates/{task_id}")

    # Process updates as they arrive
    for msg in messages:
        if msg.data.startswith(": "):
            continue
        else:
            try:
                data = parse_sse_data(msg.data)
                print(data)
            except json.JSONDecodeError:
                    print(f'Invalid JSON: {msg.data}')
        # Check if the task is done
        if data['status'] == 'done':
            # Get the final output
            final_output = data['final_output']

            title = final_output['title']
            print(f'Title: {title}')

            # Get the length of the parsed_text_description list
            n = len(final_output['parsed_text_description'])

            # Loop through to write each page
            for i in range(n):

                # assign
                page_text = final_output['parsed_text_description'][i]
                caption = final_output['parsed_image_description'][i]
                image = base64_to_image(final_output['illustrations'][i])

                # display
                print(f'Page {i+1}:  \n{page_text}')
                print(caption)
                # image.show

            # Exit the loop when the task is done
            break
        else:
            # Update the frontend with the latest available data
            if 'final_output' in data:
                title = data['final_output']['title']
                print(f'Title: {title}')

                # Get the length of the parsed_text_description list
                n = len(data['final_output']['parsed_text_description'])

                # Loop through to write each page
                for i in range(n):

                    # assign
                    page_text = data['final_output']['parsed_text_description'][i]
                    caption = data['final_output']['parsed_image_description'][i]
                    image = base64_to_image(data['final_output']['illustrations'][i])

                    # display
                    print(f'Page {i+1}:  \n{page_text}')
                    print(caption)
                    # image.show
