#!/usr/bin/bash

python manage.py migrate
python manage.py loaddata hydrogenaseclass hydrogenasesequence
python manage.py train
python manage.py trainupstream data
