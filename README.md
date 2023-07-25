# Rotate-Calvary
Backend for a web application that uses AI to generate storybooks given user inputs, including a description (the main idea of the story) and the total number of pages.

### Documentation and Demo
- [Backend OpenAPI Documentation](https://rotate-calvary.fly.dev/docs)
- [Try the Front-end Demo](https://storybook-generator.vercel.app/)

### Tech Stack
The application uses:
- Python: The main language used for the backend server
- FastAPI: The web framework used to handle HTTP requests and responses, data validation, serialization, dependency injection, and asynchronous background tasks
- OpenAI API: Interacts with the GPT-4 model to generate text and prompts
- Python-dotenv: Handles the loading and reading of environment variables, like API keys
- LangChain: Language model integration framework used to facilitate OpenAI model interaction
- SSE-Starlette: Provides Server-Sent Events (SSE) support
- Security Libraries: Python's built-in secrets library is used to enable basic authorization
- Docker: Used for creating, deploying, and running the application using containerization
- Fly.io: The cloud platform where the application is deployed

### High-Level Process Overview

1. A client requests a new storybook with a description and a total number of pages using the `/get_storybook/` endpoint.
2. This triggers the `generate_storybook` function in a new background task, which begins by sending an update with status as 'working' and progress as 0.
3. The function checks the provided user input against an OpenAI moderation model to ensure it's appropriate.
4. If the input passes the moderation check, the function uses a series of calls to the OpenAI API to generate a title, text descriptions for each page, and image descriptions for each page.
5. For each step in the process, the function sends an update with the current progress and the data generated so far, so that the frontend can update.
6. Once the text generation process is complete, the function starts generating illustrations based on the image descriptions.
7. The generated illustrations are uploaded to an S3 bucket (with expire policy) so that links can be included in the updates and final output.
8. Once all illustrations have been generated, the function sends a final update with status as 'done', closes the SSE connection, and builds a `final_output` object containing all the generated data.
9. The client can get updates on the progress of their request by connecting to the `/get_updates/{task_id}` endpoint, which returns an event stream of updates.
10. The client can get the final output by using the `/get_final_output` endpoint.
11. After a delay, the task containing the data for the request is deleted.

### Customization
You can use OpenAI's DALLE2 to generate the images instead of StabilityAI's SDXL by changing `main.py` to import `generate_illustration` from `generate_illustration_openai` instead of `generate_illustration_stabilityai`.

### Areas for Improvement

1. **Illustration consistency**: There's currently no mechanism to get the style and characters to appear the same way from one image to the next. This could be done by using the first image as the seed for the second and so on, or by refining the way the image descriptions are generated.
2. **Cover page**: Having this back-end provide a cover image could enable the front-end to show the story in more of a 3D picture book style.
3. **Text streaming**: Seeing the text show up on the page word-by-word would be much cooler than the current implementation where all the text for all the pages shows up at once. This would require some changes, but OpenAI does offer a streaming response option to make this possible.
4. **Improve response time**: This could be overall speed improvements or just improvements to how long it takes to provide a completed page 1.
5. **Add parameters**: Adding more levers to pull on the front-end could make things more interesting for users. Good candidates for parameters to add would give users control over technical factors such as model used, model temperature, and LORA applied. Another possibility would be to add parameters that interact with the prompts to give users control over story-related factors such as main character name, main character appearance, setting, etc.
