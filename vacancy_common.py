from terminaltables import AsciiTable


def get_vacancies_names():
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


def print_salary_table(title, language_stats):
    table_data = [
        ["Language", "Found vacancies", "Processed", "Average salary"]
    ]
    for language, stats in language_stats.items():
        row = [
            language,
            str(stats["vacancies_found"]),
            str(stats["vacancies_processed"]),
            str(stats["average_salary"])
        ]
        table_data.append(row)
    table = AsciiTable(table_data, title)
    print(table.table)
