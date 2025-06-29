# Use the official Python image as the base
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Ensure .env is copied (if present)
COPY .env .env

# Expose the port FastAPI will run on
EXPOSE 8000

# Start FastAPI app with uvicorn, auto-reload for dev (remove --reload for prod)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
