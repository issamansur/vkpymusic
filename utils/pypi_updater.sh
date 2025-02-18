#!/bin/bash

# !!! Execute from the root of the repository

pip install poetry

# Install dependencies
poetry install 

# Ask user to continue
read -sp "Input your PyPI token: " TOKEN
export POETRY_PYPI_TOKEN_PYPI="$TOKEN"

# Build and publish package
poetry publish --build
