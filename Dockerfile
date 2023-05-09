# Dockerfile
FROM python:3.9-slim-buster

WORKDIR /routebots_10

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]





