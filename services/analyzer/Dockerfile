# services/analyzer/Dockerfile
# Use CUDA base image for GPU support on Cloud Run
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

# Install Python 3.11
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    && rm -rf /var/lib/apt/lists/*

# Set python3.11 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Cloud Run sets PORT env variable
ENV PORT=8080

# Run with uvicorn, binding to 0.0.0.0 and using PORT env
CMD python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT}
