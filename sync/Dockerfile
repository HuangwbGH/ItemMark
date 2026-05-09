FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    freetds-dev \
    freetds-bin \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY sync/freetds.conf /etc/freetds/freetds.conf

WORKDIR /app

COPY sync/requirements.txt ./sync/requirements.txt
RUN pip install --no-cache-dir -r ./sync/requirements.txt

COPY sync ./sync
COPY config ./config

CMD ["python", "sync/scheduler.py"]

