FROM continuumio/miniconda3:4.4.10

LABEL maintainer="Dan Søndergaard <das@birc.au.dk>"

ENV PYTHONUNBUFFERED 1

RUN echo "deb http://archive.debian.org/debian stretch main contrib non-free" > /etc/apt/sources.list
RUN apt-get update && apt-get -y install libgl1-mesa-glx && \
    apt-get remove --purge && \
    rm -rf /var/lib/apt/lists/*

# COPY environment.yml environment.yml
# RUN conda upgrade -n base conda && \
#     conda env create -q -f environment.yml && \
#     conda clean -y -i -l -t -p

COPY environment_v2.yml environment_v2.yml
RUN conda upgrade -n base conda && \
    conda env create -q -f environment_v2.yml && \
    conda clean -y -i -l -t -p

COPY . /code
WORKDIR /code

ENV PATH /opt/conda/envs/hyddb/bin:$PATH

CMD ["gunicorn", "-b", "0.0.0.0", "hyddb.wsgi"]
