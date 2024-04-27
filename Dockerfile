FROM python:3.11.7
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /Users/murillo/repos/fast_zero/
COPY . .

RUN chmod +x ./entrypoint.sh

RUN pip install poetry

RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi

EXPOSE 8000
CMD poetry run uvicorn --host 0.0.0.0 fast_zero.app:app