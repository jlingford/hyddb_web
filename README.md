# Instructions

## Running with Docker

First build the Docker image:

```bash
docker build -t "dansondergaard/hyddb" .
```

Alternatively, just pull the image from Docker Hub:

```bash
docker pull dansondergaard/hyddb
```

To run the web service, modify the environment variables in
`docker-compose.yml` to fit your development environment and then run:

```bash
docker-compose up -d
```

Now run the database migrations.

```bash
docker-compose run web python manage.py migrate
```

Then load the fixtures.

```bash
docker-compose run web python manage.py loaddata hydrogenaseclass hydrogenasesequence
```

Then train the two classifiers.

```bash
docker-compose run web python manage.py train
docker-compose run web python manage.py trainupstream data
```

## Running without Docker

Requires miniconda or micromamba for managing virtual environments

First, create and activate the conda environment:

```bash
conda env create -f environment.yml
conda activate hyddb_env1
pip install parso==0.7.0

# parso needs to be downgraded to be compatible with python 3.5

```

Second, setup the Django server and train the classifier:

```bash
python manage.py migrate
python manage.py loaddata hydrogenaseclass hydrogenasesequence
python manage.py train
python manage.py trainupstream data

```

Third, launch the website locally:

```bash
python manage.py runserver 127.0.0.1:8000

```

Now open `http://127.0.0.1:8000` in a browser, preferably Firefox
