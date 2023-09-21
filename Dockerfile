FROM python:3.9

RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY ./app /code/app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
