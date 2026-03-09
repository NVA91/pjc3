FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . /app

RUN mkdir -p /app/data /app/config /app/cache /app/tmp /run/secrets \
    && chmod 1777 /app/tmp

CMD ["sleep", "infinity"]
