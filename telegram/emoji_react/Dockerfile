# Use official Python image
FROM python:3.12-slim

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY app/pyproject.toml app/poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application code
COPY app/ .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["poetry", "run", "python", "main.py"]
