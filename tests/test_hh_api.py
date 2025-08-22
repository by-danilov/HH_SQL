import unittest
from unittest.mock import patch, Mock
from src.hh_api import HHApi
import requests


class TestHHApi(unittest.TestCase):
    """
    Класс для тестирования модуля hh_api.
    """

    def setUp(self):
        self.companies = ["Сбербанк", "Яндекс"]
        self.hh_api = HHApi(self.companies)

    @patch('requests.get')
    def test__get_companies_id(self, mock_get):
        """
        Тестирует получение ID компаний с мокированием API-запроса.
        """
        # Настройка мока для имитации ответа API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'id': '1234', 'name': 'Сбербанк', 'alternate_url': 'sberbank_url'}
            ]
        }
        mock_get.return_value = mock_response

        companies = self.hh_api._get_companies_id()

        self.assertIn('Сбербанк', companies)
        self.assertEqual(companies['Сбербанк']['id'], 1234)

    @patch('requests.get')
    def test_get_vacancies(self, mock_get):
        """
        Тестирует метод get_vacancies.
        """
        # Настройка мока для имитации ответа API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [{'id': '1', 'name': 'Vacancy 1'}, {'id': '2', 'name': 'Vacancy 2'}],
            'pages': 1
        }
        mock_get.return_value = mock_response

        vacancies = self.hh_api.get_vacancies()

        self.assertIn('Сбербанк', vacancies)
        self.assertIsInstance(vacancies['Сбербанк'], list)
        self.assertEqual(len(vacancies['Сбербанк']), 2)


if __name__ == '__main__':
    unittest.main()
