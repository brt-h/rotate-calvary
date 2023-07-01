# rotate-calvary
# https://storybook-generator.vercel.app/

Backend for a web application that uses AI to generate storybooks given user inputs, including a description (the main idea of the story) and the total number of pages.

The application uses the FastAPI framework to define endpoints, asyncio for asynchronous operations, and various custom classes and functions to interact with the OpenAI API, parse and format responses, and perform various operations like converting images to base64 strings.

Here's a high-level overview of the process:

    1. A client requests a new storybook with a description and a total number of pages using the /get_storybook/ endpoint.
    2. This triggers the generate_storybook function in a new background task, which begins by sending an update with status as 'working' and progress as 0.
    3. The function checks the provided user input against an OpenAI moderation model to ensure it's appropriate.
    4. If the input passes the moderation check, the function uses a series of calls to the OpenAI API to generate a title, text descriptions for each page, and image descriptions for each page.
    5. For each step in the process, the function sends an update with the current progress and the data generated so far.
    6. Once the text generation process is complete, the function starts generating illustrations based on the image descriptions.
    7. The generated illustrations are converted to base64 strings so they can be included in the updates and final output.
    8. Once all illustrations have been generated, the function sends a final update with status as 'done', and builds a final_output object containing all the generated data.
    9. The client can get updates on the progress of their request by connecting to the /get_updates/{task_id} endpoint, which returns an event stream of updates.
    10. The client can get the final output by using the /get_final_output endpoint.