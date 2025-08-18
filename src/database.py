import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv


def create_database(db_name: str, params: dict):
    """Создает новую базу данных."""
    conn = None
    try:
        conn = psycopg2.connect(dbname='postgres', **params)
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
        cur.execute(
            sql.SQL("CREATE DATABASE {} WITH ENCODING 'UTF8' TEMPLATE template0").format(sql.Identifier(db_name)))

        print(f"База данных {db_name} успешно создана.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при создании базы данных: {error}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()


def create_tables(db_name: str, params: dict):
    """Создает таблицы `companies` и `vacancies`."""
    conn = None
    try:
        conn = psycopg2.connect(dbname=db_name, **params)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE companies (
                company_id INTEGER PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                url VARCHAR(255)
            )
        """)
        print("Таблица `companies` успешно создана.")

        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES companies(company_id),
                vacancy_name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url VARCHAR(255)
            )
        """)
        print("Таблица `vacancies` успешно создана.")

        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при создании таблиц: {error}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()


if __name__ == '__main__':
    load_dotenv()
    db_params = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
    }
    db_name = os.getenv("DB_NAME")

    create_database(db_name, db_params)
    create_tables(db_name, db_params)
