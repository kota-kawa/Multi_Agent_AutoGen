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

# 開発時: gunicorn with reload, 本番時: gunicorn without reload
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--workers", "1", "--threads", "4", "--timeout", "120", "--reload"]
