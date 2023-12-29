# Use specialized FastAPI+Uvicorn+Gunicorn image
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Set PYTHONPATH environment variable
ENV PYTHONPATH "${PYTHONPATH}:/"
ENV PORT=8000

# Install Poetry
RUN pip install poetry

# Set poetry virtualenv creation to false and install dependencies
RUN poetry config virtualenvs.create false

# Copy pyproject.toml and poetry.lock files
COPY ./pyproject.toml ./poetry.lock* /app/

# Install dependencies without installing the root package or dev dependencies
RUN poetry install --no-root --no-dev

# Copy the rest of the code
COPY ./app /app
