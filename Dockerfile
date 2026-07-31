FROM python:3.11-slim

# Install system dependencies & Playwright OS libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser binaries
RUN python -m playwright install chromium

# Copy application source code
COPY . .

# Expose Streamlit port
EXPOSE 8501

ENV PYTHONPATH=/app
ENV BROWSER_HEADLESS=true

CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
