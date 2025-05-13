# Programming vacancies compare #

This project collects and compares salary statistics for popular programming languages using data from HeadHunter and SuperJob APIs. It calculates the average salary for each language, counts vacancies, and displays the results in tables.

## How to install ##

1. After cloning repository you should create a virtual environment and install dependencies:

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

2. Add `.env` file with your SuperJob API token:

    ```
    SUPERJOB_TOKEN=your_token_here
    ```

3. After these two steps, you can run the scripts:

    ```bash
    python hh_stats.py
    python superjob_stats.py
    ```

## Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org).
