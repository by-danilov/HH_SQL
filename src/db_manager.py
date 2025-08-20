import psycopg2
from typing import List, Dict, Any


class DBManager:
    """
    Класс для управления данными в базе данных PostgreSQL.
    """
    def __init__(self, db_name: str, params: dict):
        """
        Инициализирует менеджер, устанавливая соединение с БД.
        :param db_name: Имя базы данных.
        :param params: Параметры подключения к БД.
        """
        self.db_name = db_name
        self.params = params

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой.
        """
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.company_name, COUNT(v.vacancy_id) AS vacancies_count
                    FROM companies c
                    LEFT JOIN vacancies v ON c.company_id = v.company_id
                    GROUP BY c.company_name;
                """)
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({"company_name": row[0], "vacancies_count": row[1]})
                return results

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        вакансии, зарплаты и ссылки на вакансию.
        """
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id;
                """)
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary_from": row[2],
                        "salary_to": row[3],
                        "url": row[4]
                    })
                return results

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        """
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT AVG(COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2
                    FROM vacancies
                    WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL;
                """)
                avg_salary = cur.fetchone()[0]
                return float(avg_salary) if avg_salary else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней.
        """
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.url
                    FROM vacancies v
                    JOIN companies c ON v.company_id = c.company_id
                    WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > (
                        SELECT AVG(COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2
                        FROM vacancies
                        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
                    );
                """)
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary_from": row[2],
                        "salary_to": row[3],
                        "url": row[4]
                    })
                return results

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список вакансий, в названии которых есть ключевое слово.
        :param keyword: Ключевое слово для поиска.
        """
        with psycopg2.connect(dbname=self.db_name, **self.params) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT c.company_name, v.vacancy_name, v.salary_from, v.salary_to, v.url FROM vacancies v JOIN companies c ON v.company_id = c.company_id WHERE v.vacancy_name ILIKE %s",
                    ('%' + keyword + '%',)
                )
                rows = cur.fetchall()
                results = []
                for row in rows:
                    results.append({
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary_from": row[2],
                        "salary_to": row[3],
                        "url": row[4]
                    })
                return results
