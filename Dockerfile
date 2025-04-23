FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app


USER appuser

EXPOSE 5000

CMD ["python", "app.py"]