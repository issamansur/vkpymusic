REM !!! Execute from the root of the repository

REM Install poetry
pip install poetry

REM Install dependencies
poetry install

REM Ask user to input PyPI token
set /p TOKEN="Input your PyPI token: "
set POETRY_PYPI_TOKEN_PYPI=%TOKEN%

REM Build and publish package
poetry publish --build