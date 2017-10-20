FROM python:3.6.2-slim
WORKDIR '/skills-labeller'

# Required system libraries
RUN apt-get update &&\
    apt-get install -y build-essential &&\
    apt-get install -y git

# Required inital python related files
ADD preprocessor/requirements.txt requirements.txt

## Install required python libraries, spacy related libary
#RUN pip install virtualenv
#RUN ln -s /usr/local/bin/virtualenv /usr/bin/virtualenv
#RUN virtualenv -p python3 env
RUN pip install -r requirements.txt --no-cache-dir
RUN python -m spacy download en
# see: https://github.com/explosion/spaCy/issues/1110 (on debian)
RUN apt-get install -y libgomp1 

# Clean up
RUN apt-get remove -y build-essential && apt-get remove -y git && apt-get -y autoremove

# Copy over preprocessor specific content
ADD preprocessor preprocessor
ADD run.sh run.sh
ADD webserver.py webserver.py
ADD Procfile Procfile
ADD runtime.txt runtime.txt
ADD setup.py setup.py

#ENV API_DEBUG=0
#ENV API_PORT=3000
#ENV API_HOST='localhost'

ENTRYPOINT '/skills-labeller/run.sh'
