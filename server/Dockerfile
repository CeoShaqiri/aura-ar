FROM python:3.11-slim

WORKDIR /app

# System packages: Tesseract OCR + Poppler (PDF→image) for Legacy Grant verification
RUN apt-get update && apt-get install -y --no-install-recommends \
      tesseract-ocr \
      tesseract-ocr-eng \
      poppler-utils \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (layer-cached)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY db.py .
COPY viewer_template.html .
COPY ocr_verify.py .

# Models are stored in a Docker volume (/data/models), not baked into the image
VOLUME ["/data/models"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
