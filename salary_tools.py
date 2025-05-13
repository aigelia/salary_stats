def predict_rub_salary(salary_info):
    result = []
    for item in salary_info:
        min_salary = item.get("from")
        max_salary = item.get("to")
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
