#!/usr/bin/bash

# for quick iterative testing in local environment without Docker.

# create conda env (do once):
#
# conda env create -f environment.yml
# conda activate hyddb_env1
# pip install parso==0.7.0
# conda deactivate

# make sure conda env is activated:
#
# conda activate hyddb_env1

# python manage.py migrate
# # python manage.py loaddata hydrogenaseclass hydrogenasesequence geneticorganisation
# python manage.py makemigrations
# python manage.py migrate browser
# python manage.py loaddata hydrogenaseclass hydrogenasesequence geneticorganisation
# python manage.py train
# python manage.py trainupstream data
# python manage.py runserver 0.0.0.0:8000

# python manage.py loaddata hydrogenaseclass hydrogenasesequence geneticorganisation
python manage.py makemigrations
python manage.py migrate
python manage.py migrate browser
python manage.py loaddata hydrogenaseclass hydrogenasesequence geneticorganisation
python manage.py train
python manage.py trainupstream data
python manage.py runserver 0.0.0.0:8000
