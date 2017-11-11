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
COPY ../test test
COPY bin bin
COPY skilloracle skilloracle
COPY api api
COPY endpoint endpoint

ADD webserver.py webserver.py
ADD run.sh run.sh

# Install specific dependencies
RUN pip install -r requirements.txt
# Install any OS utilities needed
RUN apt-get -y install psmisc 

#RUN chmod a+x run.sh
#ENTRYPOINT ["./run.sh"]
