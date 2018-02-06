FROM picoded/ubuntu-openjdk-8-jdk:16.04
MAINTAINER "Kwame Porter Robinson" kporterrobinson@gmail.com

RUN apt-get update &&\
    apt-get -y install git build-essential libboost-program-options-dev libboost-python-dev zlib1g-dev  &&\
    git clone git://github.com/JohnLangford/vowpal_wabbit.git /vowpal_wabbit &&\
    cd /vowpal_wabbit && make && make install &&\
    rm -Rf /vowpal_wabbit/* &&\ 
    apt-get -y autoremove

RUN apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Python 3 seemingly not available in openjdk:8-jdk
RUN apt-get update && apt-get -y upgrade &&\
    apt-get -y install python3 python3-pip libssl-dev libffi-dev python3-dev
# note: https://github.com/Homebrew/legacy-homebrew/issues/25752, overwrites pip w/ pip3
# Use pip going forward until this hack is resolved
RUN pip3 install --upgrade pip setuptools

WORKDIR '/skills-labeller'
# Install a variety of dependencies
ADD skilloracle/requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get -y install psmisc 
RUN apt-get -y install netcat

# Copy over the rest of the source
COPY skilloracle skilloracle
COPY test test

RUN chmod a+x /skills-labeller/skilloracle/run.sh
ENTRYPOINT ["/skills-labeller/skilloracle/run.sh"]
