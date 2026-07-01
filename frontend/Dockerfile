FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit","run","frontend.py","--server.address=0.0.0.0","--server.port=8501"]