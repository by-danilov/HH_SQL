import requests
from typing import List, Dict, Any


class HHApi:
    """
    Класс для взаимодействия с API hh.ru.
    Позволяет получать информацию о компаниях и их вакансиях.
    """
    def __init__(self, company_names: List[str]):
        """
        Инициализирует API-клиент.

        :param company_names: Список названий компаний для поиска.
        """
        self.base_url = "https://api.hh.ru/"
        self.company_names = company_names
        self.companies = self._get_companies_id()

    def _get_companies_id(self) -> Dict[str, Any]:
        """
        Получает ID компаний по их названиям.
        """
        companies_data = {}
        for name in self.company_names:
            response = requests.get(f"{self.base_url}employers", params={'text': name, 'per_page': 1})
            if response.status_code == 200:
                items = response.json().get('items', [])
                if items:
                    company = items[0]
                    companies_data[name] = {
                        "id": int(company.get('id')),
                        "name": company.get('name'),
                        "url": company.get('alternate_url')
                    }
        return companies_data

    def get_vacancies(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получает вакансии для каждой компании из списка.
        """
        vacancies_data = {}
        for company_name, company_info in self.companies.items():
            company_id = company_info['id']
            vacancies = []
            page = 0
            while True:
                response = requests.get(
                    f"{self.base_url}vacancies",
                    params={'employer_id': company_id, 'page': page, 'per_page': 100}
                )
                if response.status_code == 200:
                    data = response.json()
                    vacancies.extend(data.get('items', []))
                    if page >= data.get('pages', 0) - 1:
                        break
                    page += 1
                else:
                    break
            vacancies_data[company_name] = vacancies
        return vacancies_data
    