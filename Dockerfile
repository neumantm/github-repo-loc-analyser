FROM python:3.8.5-slim-buster

RUN apt update && apt install -y \
    unzip \
    git \
    cloc \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -


# Creating Application Source Code Directory
RUN mkdir -p /usr/src/app

# Setting Home Directory for containers
WORKDIR /usr/src/app

# Installing python dependencies
COPY pyproject.toml /usr/src/app/
COPY poetry.lock /usr/src/app/
RUN poetry install

# Copying src code to Container
COPY ./github_repo_loc_analyser/ /usr/src/app

CMD python github_repo_loc_analyzser/code_analyzer.py
