FROM python:3.9.1 as base

WORKDIR /app

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.0.9

# install poetry
RUN wget -qO- https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python\
 && echo 'export PATH=$PATH:$HOME/.poetry/bin' > /etc/profile.d/poetry.sh\
 && $HOME/.poetry/bin/poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN mkdir -p kaori/ \
 && touch kaori/__init__.py \
 && $HOME/.poetry/bin/poetry install --no-dev

FROM base as production

COPY . .

FROM base as development

RUN $HOME/.poetry/bin/poetry install
