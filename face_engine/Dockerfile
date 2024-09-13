FROM python:3.9

WORKDIR /app

RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

COPY face_engine/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY .env /app/
COPY face_engine/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-certfile", "/ssl/cert.pem", "--ssl-keyfile", "/ssl/key.pem"]
