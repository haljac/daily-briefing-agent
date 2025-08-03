FROM astral/uv:python3.13-bookworm-slim

WORKDIR /app

COPY . /app

RUN uv sync
