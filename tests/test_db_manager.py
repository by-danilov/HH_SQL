import unittest
import os
import psycopg2
from dotenv import load_dotenv

from src.db_manager import DBManager
from src.database import create_database, create_tables
from src.hh_api import HHApi
from src.main import insert_data_to_db


class TestDBManager(unittest.TestCase):
    """
    Класс для тестирования методов DBManager.
    """

    @classmethod
    def setUpClass(cls):
        """
        Настройка тестовой базы данных и загрузка данных.
        Выполняется один раз перед всеми тестами.
        """
        load_dotenv()
        cls.db_params = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
        }
        cls.test_db_name = "test_hh_vacancies"

        # Создание и заполнение тестовой БД
        create_database(cls.test_db_name, cls.db_params)
        create_tables(cls.test_db_name, cls.db_params)

        company_names = [
            "ООО Синара-Девелопмент", "ПАО МегаФон", "Петрович, Строительный Торговый Дом"
        ]
        hh_api_client = HHApi(company_names)
        companies_data = hh_api_client.companies
        vacancies_data = hh_api_client.get_vacancies()
        all_data = {"companies": companies_data, "vacancies": vacancies_data}
        insert_data_to_db(cls.test_db_name, cls.db_params, all_data)

        cls.db_manager = DBManager(cls.test_db_name, cls.db_params)

    @classmethod
    def tearDownClass(cls):
        """
        Удаление тестовой базы данных.
        Выполняется один раз после всех тестов.
        """
        conn = None
        try:
            conn = psycopg2.connect(dbname='postgres', **cls.db_params)
            conn.autocommit = True
            cur = conn.cursor()
            cur.execute(f"DROP DATABASE {cls.test_db_name}")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Ошибка при удалении тестовой базы данных: {error}")
        finally:
            if conn is not None:
                cur.close()
                conn.close()

    def test_get_companies_and_vacancies_count(self):
        """
        Тестирует метод get_companies_and_vacancies_count.
        """
        result = self.db_manager.get_companies_and_vacancies_count()
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0]['company_name'], str)
        self.assertIsInstance(result[0]['vacancies_count'], int)

    def test_get_all_vacancies(self):
        """
        Тестирует метод get_all_vacancies.
        """
        result = self.db_manager.get_all_vacancies()
        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0]['vacancy_name'], str)

    def test_get_avg_salary(self):
        """
        Тестирует метод get_avg_salary.
        """
        avg_salary = self.db_manager.get_avg_salary()
        self.assertIsInstance(avg_salary, float)
        self.assertTrue(avg_salary >= 0)

    def test_get_vacancies_with_higher_salary(self):
        """
        Тестирует метод get_vacancies_with_higher_salary.
        """
        result = self.db_manager.get_vacancies_with_higher_salary()
        # Проверка, что результат является списком
        self.assertIsInstance(result, list)

    def test_get_vacancies_with_keyword(self):
        """
        Тестирует метод get_vacancies_with_keyword.
        """
        keyword = "Python"
        result = self.db_manager.get_vacancies_with_keyword(keyword)
        self.assertIsInstance(result, list)
        if result:
            self.assertIn(keyword.lower(), result[0]['vacancy_name'].lower())


if __name__ == '__main__':
    unittest.main()
