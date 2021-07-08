
FROM python:3.9 AS python_env

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV ;\
    pip install --upgrade pip ;


FROM python_env

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=python_env /opt/venv /opt/venv


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

WORKDIR /generator

COPY --from=generator-base /upload/ /upload

ADD run.sh packet_2.py qpsk_ccsds.grc qpsk_ccsds.py /generator/

CMD ["/generator/run.sh"]

