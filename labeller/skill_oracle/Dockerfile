FROM ardinor/centos-python3.4.2
MAINTAINER "Kwame Porter Robinson" <kporterrobinson@gmail.com>
RUN yum -y update; yum clean all
# Install JDK (for vowpal wabbit)
RUN yum install -y \
       java-1.8.0-openjdk \
       java-1.8.0-openjdk-devel
ENV JAVA_HOME /etc/alternatives/jre

# Install Vowpal Wabbit
RUN yum -y install git gcc-c++ make boost-devel zlib-devel clang-devel which &&\
    git clone git://github.com/JohnLangford/vowpal_wabbit.git /vowpal_wabbit &&\
    cd /vowpal_wabbit && make && make install &&\
    rm -Rf /vowpal_wabbit/* && yum -y remove git gcc-c++ make boost-devel zlib-devel clang-devel which &&\
    yum clean all
WORKDIR /vowpal_wabbit

# Install Python packages (really only need pymongo though)
ADD requirements ../../requirements
ADD requirements.txt ../../requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
RUN yum -y update; yum clean all

# Copy over Oracle script
COPY run.sh /vowpal_wabbit
RUN chmod a+x run.sh
ENTRYPOINT ["/vowpal_wabbit/run.sh"]
