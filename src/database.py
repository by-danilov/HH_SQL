import psycopg2
from psycopg2 import sql


def create_database(db_name: str, params: dict) -> None:
    """
    Создает новую базу данных в PostgreSQL.
    """
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


def create_tables(db_name: str, params: dict) -> None:
    """
    Создает таблицы `companies` и `vacancies` в указанной базе данных.
    """
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
