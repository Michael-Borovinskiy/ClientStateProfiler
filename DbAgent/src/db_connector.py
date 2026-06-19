import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

def get_db_connection():

    current_dir = Path(__file__).resolve().parent
    dotenv_path = current_dir.parent / 'config' / '.env'
    load_dotenv(dotenv_path=dotenv_path)

    """Создаёт и возвращает подключение к PostgreSQL."""
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    dbname = os.getenv("POSTGRES_DB")

    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname
    )
    return conn


def execute_sql_query(sql: str) -> tuple[list[tuple], list[str]]:
    """
    Выполняет SQL-запрос и возвращает (rows, column_names).
    Для SELECT возвращает данные; для INSERT/UPDATE/DELETE фиксирует транзакцию.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            # Если это SELECT-подобный запрос, возвращаем колонки и строки
            if cur.description:
                column_names = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                return rows, column_names
            else:
                # INSERT/UPDATE/DELETE — commit
                conn.commit()
                return [], []
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()