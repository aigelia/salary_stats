def predict_rub_salaries(salary_entries):
    result = []
    for salary_entry in salary_entries:
        min_salary = salary_entry.get("from")
        max_salary = salary_entry.get("to")
        if min_salary and max_salary:
            average = (min_salary + max_salary) / 2
        elif min_salary:
            average = min_salary * 1.2
        elif max_salary:
            average = max_salary * 0.8
        else:
            continue
        result.append(average)
    return result


def calculate_average_salary(salaries):
    count = len(salaries)
    if count == 0:
        return 0, 0
    average = int(sum(salaries) / count)
    return average, count
