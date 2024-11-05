FROM python:3.12.2-bullseye

RUN pip install --upgrade pip
RUN pip install poetry

RUN poetry config virtualenvs.create false

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root && rm -rf $POETRY_CACHE_DIR


# Not needed since we are running from a volume
# COPY . usr/src/app

# RUN poetry install
