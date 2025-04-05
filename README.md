# Instructions

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
docker-compose run web python manage.py trainupstream
```
