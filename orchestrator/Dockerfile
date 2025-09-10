FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 必要に応じてビルド系（多くの環境で不要ですが保険として）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --no-cache-dir -r /app/requirements.txt


COPY . /app

EXPOSE 8000

# Flask development server with auto-reload
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
CMD ["python", "app.py"]
