FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY source ./source

CMD ["python", "-m", "source.generator.live_generator"]
