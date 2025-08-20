FROM python:slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATA_PATH=/app/data

RUN apt update && \
    apt install -y tini && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

WORKDIR /app

COPY *.py /app
COPY app /app/app

ENV FLASK_ENV=production

ENTRYPOINT ["tini", "--"]

CMD ["python", "app.py"]
