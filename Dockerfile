FROM python:3.9

WORKDIR /code

COPY . .

# Install any needed packages specified in Pipfile.lock
RUN pip install --trusted-host pypi.python.org pipenv
RUN pipenv install --system --deploy

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]