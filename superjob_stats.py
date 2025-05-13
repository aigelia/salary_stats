from decouple import config
import requests

from vacancy_common import get_vacancy_names, print_salary_table
from salary_tools import predict_rub_salary, calculate_average_salary


def search_vacancies(api_key, vacancy_name):
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
    }

    all_objects = []
    page = 0

    while True:
        params = {
            "keyword": vacancy_name,
            "town": "Москва",
            "no_agreement": 1,
            "not_archive": True,
            "count": 100,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        all_objects.extend(data.get("objects", []))

        if not data.get("more"):
            break
        page += 1

    return {
        "found": data.get("total", 0),
        "items": all_objects
    }


def extract_salaries(vacancy_data):
    return [
        {"from": item.get("payment_from"), "to": item.get("payment_to")}
        for item in vacancy_data["items"]
        if item.get("payment_from") or item.get("payment_to")
    ]


def main():
    api_key = config("SUPERJOB_TOKEN")
    vacancy_names = get_vacancy_names()
    average_salaries = {}

    for vacancy_name in vacancy_names:
        print(f"Обрабатываю: {vacancy_name}")
        try:
            api_response = search_vacancies(api_key, vacancy_name)
            vacancies_found = api_response.get("found", 0)
            salaries_data = extract_salaries(api_response)
            salary_list = predict_rub_salary(salaries_data)
            average, count = calculate_average_salary(salary_list)

            average_salaries[vacancy_name] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": count,
                "average_salary": average
            }
        except requests.exceptions.HTTPError as e:
            print(f"Ошибка при запросе для {vacancy_name}: {e}")
            average_salaries[vacancy_name] = {
                "vacancies_found": 0,
                "vacancies_processed": 0,
                "average_salary": 0
            }

    print_salary_table("SuperJob Moscow", average_salaries)


if __name__ == "__main__":
    main()
