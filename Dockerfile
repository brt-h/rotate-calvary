# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container to /code
WORKDIR /code

# Install pipenv
RUN pip install --trusted-host pypi.python.org pipenv

# Copy only the Pipfile and Pipfile.lock to leverage Docker cache
COPY Pipfile Pipfile.lock ./

# Install any needed packages specified in Pipfile.lock
RUN pipenv install --system --deploy

# Copy the current directory contents into the container at /code
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NAME World

# Run uvicorn when the container launches
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]