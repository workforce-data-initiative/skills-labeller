FROM python:3.6.2-slim
WORKDIR '/skills-labeller'
ADD requirements requirements
ADD requirements.txt requirements.txt
RUN apt-get update && apt-get install -y build-essential && apt-get install -y git
RUN pip install -r requirements.txt --no-cache-dir
RUN apt-get remove -y build-essential && apt-get remove -y git && apt-get -y autoremove