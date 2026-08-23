FROM python:3.11-slim

WORKDIR /app

# Upgrade system packages to pull latest Debian OS security patches
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
