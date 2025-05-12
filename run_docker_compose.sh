#!/usr/bin/bash

docker compose up -d
docker compose run web python manage.py migrate
docker compose run web python manage.py loaddata hydrogenaseclass hydrogenasesequence
docker compose run web python manage.py train
docker compose run web python manage.py trainupstream data
