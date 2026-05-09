FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    freetds-dev \
    freetds-bin \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY web/requirements.txt ./web/requirements.txt
RUN pip install --no-cache-dir -r ./web/requirements.txt

COPY web ./web
COPY sync ./sync
COPY config ./config

EXPOSE 18089

CMD ["python", "-m", "web.main"]

