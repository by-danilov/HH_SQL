import unittest
import os
import psycopg2
from dotenv import load_dotenv

from src.database import create_database, create_tables


class TestDatabase(unittest.TestCase):
    """
    Класс для тестирования модуля database.
    """
    @classmethod
    def setUpClass(cls):
        """
        Устанавливает параметры для тестов.
        """
        load_dotenv()
        cls.db_params = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
        }
        cls.test_db_name = "test_db_creation"

    def tearDown(self):
        """
        Удаляет тестовую базу данных после каждого теста.
        """
        conn = None
        try:
            conn = psycopg2.connect(dbname='postgres', **self.db_params)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"DROP DATABASE IF EXISTS {self.test_db_name}")
        except (Exception, psycopg2.DatabaseError) as error:
            pass # Игнорируем ошибку, если БД не существует
        finally:
            if conn is not None:
                cur.close()
                conn.close()

    def test_create_database(self):
        """
        Тестирует создание базы данных.
        """
        create_database(self.test_db_name, self.db_params)
        conn = None
        try:
            conn = psycopg2.connect(dbname=self.test_db_name, **self.db_params)
            self.assertIsNotNone(conn)
        except Exception:
            self.fail("Не удалось подключиться к созданной базе данных.")
        finally:
            if conn is not None:
                conn.close()

    def test_create_tables(self):
        """
        Тестирует создание таблиц.
        """
        create_database(self.test_db_name, self.db_params)
        create_tables(self.test_db_name, self.db_params)
        conn = None
        try:
            conn = psycopg2.connect(dbname=self.test_db_name, **self.db_params)
            cur = conn.cursor()
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            tables = [table[0] for table in cur.fetchall()]
            self.assertIn('companies', tables)
            self.assertIn('vacancies', tables)
        finally:
            if conn is not None:
                cur.close()
                conn.close()
