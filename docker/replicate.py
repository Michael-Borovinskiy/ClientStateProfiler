
import os
import time
import psycopg2
from clickhouse_driver import Client

def get_postgres_connection():
    return psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        dbname=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )

def get_clickhouse_connection():
    return Client(
        host='localhost',
        user=os.environ['CLICKHOUSE_DEFAULT_USER'],
        password=os.environ['CLICKHOUSE_DEFAULT_PASSWORD']
    )

def replicate_data():
    pg_conn = get_postgres_connection()
    ch_client = get_clickhouse_connection()

    ch_client.execute("""
    CREATE TABLE IF NOT EXISTS expertises (
        expertise_type String,
        client_id String,
        status String,
        comment String,
        dt_expertise_status DateTime
    ) ENGINE = MergeTree()
    ORDER BY dt_expertise_status
    """)

    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT expertise_type, client_id, status, comment, dt_expertise_status FROM expertises")
    data = pg_cursor.fetchall()
    pg_cursor.close()
    pg_conn.close()

    if data:
        ch_client.execute("TRUNCATE TABLE expertises")
        ch_client.execute("INSERT INTO expertises VALUES", data)

if __name__ == "__main__":
    while True:
        replicate_data()
        time.sleep(240)
