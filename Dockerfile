FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt Makefile .
RUN make install && make test && make format && make lint
#pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/* tests/* .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

#EXPOSE 3000

#CMD ["python",  "src/main.py"]
