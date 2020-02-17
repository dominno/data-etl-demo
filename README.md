
Advertising Data ETL demo

How to install:

 - create virtual env on Python 3
 - pip install -r requirements.txt
 - cp .env.example .env
 - set data url in var ETL_CSV_URL in .env file
 - ./manage.py migrate
 - ./manage.py run_data_importer
 - ./manage.py runserver
 - open http://127.0.0.1:8000/metrics/
 
 
