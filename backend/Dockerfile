FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh","-c","uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]