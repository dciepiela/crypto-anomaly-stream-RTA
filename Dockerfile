FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    openjdk-17-jdk-headless \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python", "producer.py"]
