FROM python:3.6.2-slim
WORKDIR '/skills-labeller'

# Required system libraries
RUN apt-get update &&\
    apt-get install -y build-essential &&\
    apt-get install -y git

# Required inital python related files
ADD etl/requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
# DEBUG: TODO: put this requirement into requirements.txt
RUN pip install pytest
RUN python -m spacy download en
# see: https://github.com/explosion/spaCy/issues/1110 (on debian)
RUN apt-get install -y libgomp1 
RUN apt-get install -y curl

# Clean up
RUN apt-get remove -y build-essential && apt-get remove -y git && apt-get -y autoremove

ADD etl etl
ADD etl/utils etl/utils
ADD resources resources
COPY test test

ENTRYPOINT '/skills-labeller/etl/run.sh'
