# Use an official lightweight Python image.
FROM python:3.14-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory in the container
WORKDIR /app

# Copy dependency files
COPY pyproject.toml .python-version ./

# Install dependencies add --frozen to ensure lockfile is used
RUN uv sync --no-dev

# Copy the content of the local src directory to the working directory
COPY src/ .

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED=1

# Set PORT environment variable (Cloud Run will override this)
ENV PORT=8080

# Command to run the FastMCP application
CMD exec uv run python main.py
