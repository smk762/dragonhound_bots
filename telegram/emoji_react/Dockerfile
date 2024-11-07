# Use an official Python image
FROM python:3.9-slim as base

# Install Poetry
RUN pip install poetry

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock to install dependencies
COPY app/pyproject.toml app/poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY app/ .

# Expose the port FastAPI will run on
EXPOSE 9524

# Command to run the FastAPI application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9524"]
