FROM python:3.12.8-slim
LABEL authors="KuyuGama"

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PIP_ROOT_USER_ACTION=ignore \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

RUN pip install poetry

WORKDIR /app

COPY ./pyproject.toml /app/

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR

COPY . /app/

CMD dramatiq redis tasks
