FROM python:3.11.7-slim-bookworm

ENV PYTHONUNBUFFERED 1

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements/ /tmp/requirements/

RUN set -x \
    && buildDeps=" \
    libffi-dev \
    libpq-dev \
    ffmpeg \
    " \
    && runDeps="" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps \
    && apt-get install -y --no-install-recommends $runDeps \
    && pip install -r /tmp/requirements/base.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app
COPY . .

RUN groupadd -r deployer && useradd -r -m -g deployer deployer && chown -R deployer:deployer /app

USER deployer
