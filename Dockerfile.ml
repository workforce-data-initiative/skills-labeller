FROM python:3.6.2-slim
MAINTAINER "Kwame Porter Robinson" kporterrobinson@gmail.com

# Install JDK
# Credit: picoded/ubuntu-openjdk-8-jdk

# Add some core repos
RUN apt-get update && \
    apt-get install -y sudo curl zip openssl build-essential python-software-properties software-properties-common && \
    apt-get clean;

RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list
RUN echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
RUN apt-get update
RUN apt-get install -y openjdk-7-jdk
RUN export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::") &&\
    ln -s $JAVA_HOME/include/jni.h /usr/include/jni.h &&\
    ln -s $JAVA_HOME/include/jni_md.h /usr/include/jni_md.h

# Install Vowpal Wabbit
RUN apt-get update &&\
    apt-get -y install git build-essential libboost-program-options-dev libboost-python-dev zlib1g-dev &&\
    git clone git://github.com/JohnLangford/vowpal_wabbit.git /vowpal_wabbit &&\
    export JAVA_HOME=$(readlink -f /usr/bin/javac | sed "s:/bin/javac::") &&\
    cd /vowpal_wabbit && make &&\
    cd /vowpal_wabbit && make install &&\
    rm -Rf /vowpal_wabbit/* &&\
    apt-get -y autoremove

RUN apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#COPY ./labeller/skill-oracle/run.sh /vowpal_wabbit
#RUN chmod a+x run.sh
#ENTRYPOINT ["/vowpal_wabbit/run.sh"]
