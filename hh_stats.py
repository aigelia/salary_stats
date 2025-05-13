import requests

from vacancy_common import get_vacancy_names, print_salary_table
from salary_tools import predict_rub_salary, calculate_average_salary


def search_vacancies(vacancy_name):
    url = "https://api.hh.ru/vacancies"
    headers = {
        "User-Agent": "studying_project/1.0"
    }
    params = {
        "text": vacancy_name,
        "area": "1",
        "period": 30,
        "per_page": 100,
        "page": 0
    }

    all_items = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        all_items.extend(data.get("items", []))

        if params["page"] >= data.get("pages", 0) - 1:
            break
        params["page"] += 1

    return {
        "found": data.get("found", 0),
        "items": all_items
    }


def extract_salaries(vacancy_data):
    return [item["salary"] for item in vacancy_data["items"] if item.get("salary")]


def main():
    vacancy_names = get_vacancy_names()
    average_salaries = {}

    for vacancy_name in vacancy_names:
        print(f"Обрабатываю: {vacancy_name}")
        try:
            api_response = search_vacancies(vacancy_name)
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

    print_salary_table("HeadHunter Moscow", average_salaries)


if __name__ == "__main__":
    main()
