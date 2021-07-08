
# FROM python:3.8.5 AS python_env

FROM python:3.9 AS python_env

FROM ubuntu:18.04 AS build

RUN apt-get update && apt-get install -y software-properties-common
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN add-apt-repository ppa:gnuradio/gnuradio-releases-3.7
RUN apt-get update
RUN apt install -y gnuradio

FROM build
# gr-ccsds OOT
RUN apt install -y git cmake
RUN git clone https://github.com/lofaldli/gr-ccsds.git \
	&& mkdir build
WORKDIR /gr-ccsds/build
RUN cmake .. -DCMAKE_INSTALL_PREFIX=$(gnuradio-config-info --prefix) \
	&& make \
	&& make install

WORKDIR /solver

COPY --from=generator-base /upload/ /upload

ADD run.sh shifttester.py qpsk_ccsds_demod.grc qpsk_ccsds_demod.py /solver/

CMD ["/solver/run.sh"]

