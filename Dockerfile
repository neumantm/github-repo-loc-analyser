FROM python:3.8.5-slim-buster

RUN apt-get update && apt install -y \
    unzip \
    git \
    cloc \
    curl \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN $HOME/.poetry/bin/poetry config virtualenvs.create false

# Creating Application Source Code Directory
RUN mkdir -p /app

# Setting Home Directory for containers
WORKDIR /app

# Installing python dependencies
COPY pyproject.toml /app
COPY poetry.lock /app
RUN $HOME/.poetry/bin/poetry install

# Copying src code to Container
COPY ./github_repo_loc_analyser /app/github_repo_loc_analyser

COPY ./.docker/docker-default-logging.conf /app

CMD $HOME/.poetry/bin/poetry run grla
