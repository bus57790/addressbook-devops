# Example: Switch to alpine or updated minimal debian image
FROM node:20-alpine

# Install system dependencies required for pyzbar / zbar
RUN apt-get update && apt-get install -y \
    libzbar0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
