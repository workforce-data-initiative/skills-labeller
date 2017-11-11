FROM openjdk:7-jdk
MAINTAINER "Kwame Porter Robinson" kporterrobinson@gmail.com

RUN apt-get update &&\
    apt-get -y install git build-essential libboost-program-options-dev libboost-python-dev zlib1g-dev  &&\
    git clone git://github.com/JohnLangford/vowpal_wabbit.git /vowpal_wabbit &&\
    cd /vowpal_wabbit && make && make install &&\
    rm -Rf /vowpal_wabbit/* &&\ 
    apt-get -y autoremove

RUN apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Python 3 seemingly not available in openjdk:7-jdk
RUN apt-get update && apt-get -y upgrade &&\
    apt-get -y install python3 python3-pip libssl-dev libffi-dev python3-dev
# note: https://github.com/Homebrew/legacy-homebrew/issues/25752, overwrites pip w/ pip3
# Use pip going forward until this hack is resolved
RUN pip3 install --upgrade pip setuptools

WORKDIR ./skilloracle
COPY ./skilloracle/bin bin
COPY ./skilloracle/skilloracle skilloracle
COPY ./skilloracle/api api
COPY ./skilloracle/endpoint endpoint
# copy above skilloralcle to main correct unittest directory structure
COPY ./test /test

ADD ./skilloracle/requirements.txt requirements.txt
ADD ./skilloracle/webserver.py webserver.py
ADD ./skilloracle/run.sh run.sh

# Install specific dependencies
RUN pip install -r requirements.txt
# Install any OS utilities needed
RUN apt-get -y install psmisc 
RUN apt-get -y install netcat

RUN chmod a+x run.sh
ENTRYPOINT ["/bin/bash"]
#ENTRYPOINT ["./run.sh"]
