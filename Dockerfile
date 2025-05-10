FROM continuumio/miniconda3:4.4.10

LABEL maintainer="Dan Søndergaard <das@birc.au.dk>"

WORKDIR /code
COPY . /code

ENV PYTHONUNBUFFERED=1

# install some old debian packages from the archive
RUN echo "deb http://archive.debian.org/debian stretch main contrib non-free" > /etc/apt/sources.list
RUN apt-get update && apt-get -y install libgl1-mesa-glx && \
    apt-get remove --purge && \
    rm -rf /var/lib/apt/lists/*

# install conda environment
COPY environment.yml environment.yml
RUN conda env create -f environment.yml

# activate conda env
RUN echo "conda activate hyddb" >> ~/.bashrc
SHELL ["/bin/bash", "--login", "-c"]

# NOTE: redundant?
ENV PATH=/opt/conda/envs/hyddb/bin:$PATH

# need to downgrade parso to work with python 3.5 since conda installs wrong version
RUN pip install parso==0.7.0

CMD ["gunicorn", "-b", "0.0.0.0", "hyddb.wsgi"]
