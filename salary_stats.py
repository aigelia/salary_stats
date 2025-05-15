import requests
from decouple import config

from vacancy_common import get_vacancies_names, print_salary_table
from salary_tools import predict_rub_salary, calculate_average_salary

MOSCOW_AREA_ID = "1"
SEARCH_PERIOD_DAYS = 30
VACANCIES_PER_PAGE = 100
EXCLUDE_NO_AGREEMENT = 1


def search_vacancies_hh(vacancy_name):
    """Fetches vacancies from HeadHunter API for a given vacancy name."""
    url = "https://api.hh.ru/vacancies"
    headers = {
        "User-Agent": "studying_project/1.0"
    }
    params = {
        "text": vacancy_name,
        "area": MOSCOW_AREA_ID,
        "period": SEARCH_PERIOD_DAYS,
        "per_page": VACANCIES_PER_PAGE,
        "page": 0
    }

    all_vacancies = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        all_vacancies.extend(response_data.get("items", []))

        if params["page"] >= response_data.get("pages", 0) - 1:
            break
        params["page"] += 1

    return response_data.get("found", 0), all_vacancies


def extract_salaries_hh(vacancies_list):
    """Extracts salary data from HeadHunter vacancy results."""
    return [vacancy["salary"] for vacancy in vacancies_list if vacancy.get("salary")]


def search_vacancies_sj(vacancy_name, api_key):
    """Fetches vacancies from SuperJob API for a given vacancy name."""
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
    }

    all_vacancies = []
    page = 0

    while True:
        params = {
            "keyword": vacancy_name,
            "town": "Moscow",
            "no_agreement": EXCLUDE_NO_AGREEMENT,
            "not_archive": True,
            "count": VACANCIES_PER_PAGE,
            "page": page
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        response_data = response.json()
        all_vacancies.extend(response_data.get("objects", []))

        if not response_data.get("more"):
            break
        page += 1

    return response_data.get("total", 0), all_vacancies


def extract_salaries_sj(vacancies_list):
    """Extracts salary data from SuperJob vacancy results."""
    return [
        {"from": vacancy.get("payment_from"), "to": vacancy.get("payment_to")}
        for vacancy in vacancies_list
        if vacancy.get("payment_from") or vacancy.get("payment_to")
    ]


def main():
    """Main function to run vacancy stats collection and output tables."""
    vacancies_names = get_vacancies_names()
    api_key = config("SUPERJOB_TOKEN")

    hh_average_salaries = {}
    for vacancy_name in vacancies_names:
        print(f"Processing data (HeadHunter): {vacancy_name}")
        try:
            vacancies_found, vacancies_list = search_vacancies_hh(vacancy_name)
            salaries_raw = extract_salaries_hh(vacancies_list)
            salary_list = predict_rub_salary(salaries_raw)
            average, count = calculate_average_salary(salary_list)
            hh_average_salaries[vacancy_name] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": count,
                "average_salary": average
            }
        except requests.exceptions.RequestException as e:
            print(f"Error while requesting HH for {vacancy_name}: {e}")
            hh_average_salaries[vacancy_name] = {
                "vacancies_found": 0,
                "vacancies_processed": 0,
                "average_salary": 0
            }

    sj_average_salaries = {}
    for vacancy_name in vacancies_names:
        print(f"Processing data (SuperJob): {vacancy_name}")
        try:
            vacancies_found, vacancies_list = search_vacancies_sj(vacancy_name, api_key)
            salaries_raw = extract_salaries_sj(vacancies_list)
            salary_list = predict_rub_salary(salaries_raw)
            average, count = calculate_average_salary(salary_list)
            sj_average_salaries[vacancy_name] = {
                "vacancies_found": vacancies_found,
                "vacancies_processed": count,
                "average_salary": average
            }
        except requests.exceptions.RequestException as e:
            print(f"Error while requesting SJ for {vacancy_name}: {e}")
            sj_average_salaries[vacancy_name] = {
                "vacancies_found": 0,
                "vacancies_processed": 0,
                "average_salary": 0
            }

    print_salary_table("HeadHunter Moscow", hh_average_salaries)
    print_salary_table("SuperJob Moscow", sj_average_salaries)


if __name__ == "__main__":
    main()
