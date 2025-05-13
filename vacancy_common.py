from terminaltables import AsciiTable


def get_vacancy_names():
    return [
        "TypeScript",
        "Swift",
        "Objective-C",
        "Java",
        "C++",
        "PHP",
        "Ruby",
        "Python",
        "JavaScript"
    ]


def print_salary_table(title, data_dict):
    table_data = [
        ["Язык", "Найдено вакансий", "Обработано", "Средняя зарплата"]
    ]
    for language, stats in data_dict.items():
        row = [
            language,
            str(stats["vacancies_found"]),
            str(stats["vacancies_processed"]),
            str(stats["average_salary"])
        ]
        table_data.append(row)
    table = AsciiTable(table_data, title)
    print(table.table)
