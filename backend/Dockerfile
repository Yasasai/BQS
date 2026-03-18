FROM python:3.11-slim

WORKDIR /app

# Install dependencies required by psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy requirements to /app/backend to match local structure
COPY requirements.txt /app/backend/
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the rest of the backend source code to /app/backend
COPY . /app/backend/

# Ensure the root /app is in PYTHONPATH so 'backend.main' works
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
