#!/usr/bin/bash

docker compose up -d
docker compose run web python manage.py makemigrations
docker compose run web python manage.py migrate
docker compose run web python manage.py migrate browser
docker compose run web python manage.py loaddata hydrogenaseclass hydrogenasesequence geneticorganisation
docker compose run web python manage.py train
docker compose run web python manage.py trainupstream data
