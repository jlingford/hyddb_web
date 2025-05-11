# HydDB

The hydrogenase database (HydDB) provides information pages for different groups of hydrogenases, and a sequence classifier tool for predicting the putative functions of input hydrogenase sequences.

The HydDB is described in Søndergaard1, Pedersen, & Chris Greening (2016) *Scientific Reports* (<https://doi.org/10.1038/srep34212>)

## Installing and hosting the HydDB locally

You can use Docker to host the website locally on your own machine.
Make sure you have Docker installed and is running (this may require running `systemctl start docker`).

### Option 1: Pull the Docker image

The first option is to pull the image from Docker Hub:

```bash
docker image pull jameslingford/hyddb-website:latest
```

### Option 2: Build and compose the Docker image from scratch

Alternatively, you can build the [Docker](https://www.docker.com) image from scratch by cloning this git repository and running Docker build:

```bash
git clone https://github.com/jlingford/hyddb_web
cd hyddb_web
docker build -t jameslingford/hyddb-website .
```

To run the web service, you may want to first modify the environment variables in
`docker-compose.yml` to fit your development environment (such as the locations of the volume directories).

First, run:

```bash
docker compose up -d
```

Second, run the database migrations:

```bash
docker compose run web python manage.py migrate
```

Third, load the fixtures:

```bash
docker compose run web python manage.py loaddata hydrogenaseclass hydrogenasesequence
```

Fourth, train the two sequence classifiers:

```bash
docker compose run web python manage.py train
docker compose run web python manage.py trainupstream data
```

### Viewing the website locally

The website should now be accessible locally at `http://0.0.0.0:8000/` or `http://127.0.0.1:8000/`.
Open the address in your internet browser (Firefox works the best in my opinion).
Happy hydrogenase hunting!

## Citation

If you use the HydDB in your research, please cite the following:

```
Søndergaard, D., Pedersen, C. N. S., & Greening, C. (2016). HydDB: A web tool for hydrogenase classification and analysis. Scientific Reports, 6(1). https://doi.org/10.1038/srep34212
```
