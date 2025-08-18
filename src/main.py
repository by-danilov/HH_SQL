import os
from dotenv import load_dotenv
from typing import Dict, Any

from src.database import create_database, create_tables
from src.hh_api import HHApi
from src.db_manager import DBManager
import psycopg2


def insert_data_to_db(db_name: str, params: dict, hh_api_data: Dict[str, Any]) -> None:
    """
    Загружает данные о компаниях и вакансиях в базу данных.
    """
    conn = None
    try:
        conn = psycopg2.connect(dbname=db_name, **params)
        cur = conn.cursor()

        companies = hh_api_data.get('companies', {})
        for company_name, company_info in companies.items():
            cur.execute(
                "INSERT INTO companies (company_id, company_name, url) VALUES (%s, %s, %s) ON CONFLICT (company_id) DO NOTHING",
                (company_info['id'], company_info['name'], company_info['url'])
            )

        vacancies_by_company = hh_api_data.get('vacancies', {})
        for company_name, vacancies in vacancies_by_company.items():
            company_id = companies[company_name]['id']
            for vacancy in vacancies:
                salary = vacancy.get('salary')
                salary_from = salary['from'] if salary and salary['from'] else None
                salary_to = salary['to'] if salary and salary['to'] else None

                cur.execute(
                    "INSERT INTO vacancies (vacancy_id, company_id, vacancy_name, salary_from, salary_to, url) VALUES (%s, %s, %s, %s, %s, %s)",
                    (vacancy['id'], company_id, vacancy['name'], salary_from, salary_to, vacancy['alternate_url'])
                )

        conn.commit()
        print("Данные успешно загружены в базу данных.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Ошибка при загрузке данных в БД: {error}")
    finally:
        if conn is not None:
            cur.close()
            conn.close()


def user_interaction(db_manager: DBManager) -> None:
    """
    Интерактивный интерфейс для работы с базой данных.
    """
    while True:
        print("\nВыберите действие:")
        print("1. Показать количество вакансий у каждой компании")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату по всем вакансиям")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Найти вакансии по ключевому слову")
        print("0. Выход")

        choice = input("Ваш выбор: ")

        if choice == '1':
            results = db_manager.get_companies_and_vacancies_count()
            print("---")
            for item in results:
                print(f"Компания: {item['company_name']}, Вакансий: {item['vacancies_count']}")
            print("---")
        elif choice == '2':
            results = db_manager.get_all_vacancies()
            print("---")
            for item in results:
                salary_info = f"Зарплата: от {item['salary_from']} до {item['salary_to']}" if item['salary_from'] or \
                                                                                              item[
                                                                                                  'salary_to'] else "Зарплата не указана"
                print(
                    f"Компания: {item['company_name']}, Вакансия: {item['vacancy_name']}, {salary_info}, Ссылка: {item['url']}")
            print("---")
        elif choice == '3':
            avg_salary = db_manager.get_avg_salary()
            print("---")
            print(f"Средняя зарплата по всем вакансиям: {avg_salary:.2f}")
            print("---")
        elif choice == '4':
            results = db_manager.get_vacancies_with_higher_salary()
            print("---")
            for item in results:
                salary_info = f"Зарплата: от {item['salary_from']} до {item['salary_to']}"
                print(
                    f"Компания: {item['company_name']}, Вакансия: {item['vacancy_name']}, {salary_info}, Ссылка: {item['url']}")
            print("---")
        elif choice == '5':
            keyword = input("Введите ключевое слово для поиска: ")
            results = db_manager.get_vacancies_with_keyword(keyword)
            print("---")
            for item in results:
                salary_info = f"Зарплата: от {item['salary_from']} до {item['salary_to']}" if item['salary_from'] or \
                                                                                              item[
                                                                                                  'salary_to'] else "Зарплата не указана"
                print(
                    f"Компания: {item['company_name']}, Вакансия: {item['vacancy_name']}, {salary_info}, Ссылка: {item['url']}")
            print("---")
        elif choice == '0':
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")

        input("Нажмите Enter, чтобы продолжить...")


def main() -> None:
    """
    Основная функция программы, которая запускает все процессы.
    """
    load_dotenv()
    db_params = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
    }
    db_name = os.getenv("DB_NAME")

    # Создание БД и загрузка данных (раскомментировать для первого запуска)
    create_database(db_name, db_params)
    create_tables(db_name, db_params)
    company_names = [
        "ООО Синара-Девелопмент", "ООО Бантер Групп", "ПАО МегаФон", "Петрович, Строительный Торговый Дом",
        "ООО Урс Групп", "ООО Брусника", "АО Уральский завод гражданской", "ВИТА. Офис",
        "ТК Интеграл+", "ООО АДС-ЭЛЕКТРО"
    ]
    hh_api_client = HHApi(company_names)
    companies_data = hh_api_client.companies
    vacancies_data = hh_api_client.get_vacancies()
    all_data = {"companies": companies_data, "vacancies": vacancies_data}
    insert_data_to_db(db_name, db_params, all_data)

    db_manager = DBManager(db_name, db_params)
    user_interaction(db_manager)


if __name__ == '__main__':
    main()
