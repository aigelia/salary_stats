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

    vacancies = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        found = response.json().get("found", 0)
        items = response.json().get("items", [])
        vacancies.extend(items)

        if params["page"] >= response.json().get("pages", 0) - 1:
            break
        params["page"] += 1

    return found, vacancies


def extract_salary_hh(vacancy_salary):
    """Extracts salary info from a single HeadHunter vacancy salary field."""
    return vacancy_salary if vacancy_salary else None


def search_vacancies_sj(vacancy_name, api_key):
    """Fetches vacancies from SuperJob API for a given vacancy name."""
    url = "https://api.superjob.ru/2.0/vacancies/"
    headers = {
        "X-Api-App-Id": api_key,
    }

    vacancies = []
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
        total = response.json().get("total", 0)
        objects = response.json().get("objects", [])
        vacancies.extend(objects)

        if not response.json().get("more"):
            break
        page += 1

    return total, vacancies


def extract_salary_sj(payment_from, payment_to):
    """Extracts and combines payment info from SuperJob vacancy fields."""
    if payment_from or payment_to:
        return {"from": payment_from, "to": payment_to}
    return None


def main():
    """Main function to run vacancy stats collection and output tables."""
    vacancies_names = get_vacancies_names()
    api_key = config("SUPERJOB_TOKEN")

    hh_average_salaries = {}
    for vacancy_name in vacancies_names:
        print(f"Processing data (HeadHunter): {vacancy_name}")
        try:
            found, vacancies = search_vacancies_hh(vacancy_name)
            salaries_raw = [extract_salary_hh(vacancy.get("salary")) for vacancy in vacancies]
            salaries_filtered = [s for s in salaries_raw if s]
            salary_list = predict_rub_salary(salaries_filtered)
            average, count = calculate_average_salary(salary_list)
            hh_average_salaries[vacancy_name] = {
                "vacancies_found": found,
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
            found, vacancies = search_vacancies_sj(vacancy_name, api_key)
            salaries_raw = [extract_salary_sj(v.get("payment_from"), v.get("payment_to")) for v in vacancies]
            salaries_filtered = [s for s in salaries_raw if s]
            salary_list = predict_rub_salary(salaries_filtered)
            average, count = calculate_average_salary(salary_list)
            sj_average_salaries[vacancy_name] = {
                "vacancies_found": found,
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
