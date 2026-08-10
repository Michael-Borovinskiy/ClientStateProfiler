FROM python:3.12-slim

WORKDIR /app

RUN pip install psycopg2-binary clickhouse-driver

COPY replicate.py .

CMD ["python", "replicate.py"]
