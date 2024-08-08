FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update && \
    apt-get install -y build-essential default-libmysqlclient-dev pkg-config && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
