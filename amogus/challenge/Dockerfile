#######################
# Challenge compiler image
#######################

# Compiles the binary, downloads python dependencies and
# downloads and extracts libc2.27

FROM phusion/baseimage:master-amd64 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386 && \
    apt-get -y update && \
    apt install -y \
    libssl-dev \
    python3-dev \
    python3-pip \
    build-essential \
    gcc \
    socat \
    git \
    patchelf \
    python3-distutils \
    wget \
    make \
    dpkg 

# Download and save libc2.27
WORKDIR /tmp
RUN wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.27-3ubuntu1.2_amd64.deb && \
    dpkg --extract libc6_2.27-3ubuntu1.2_amd64.deb libc6_2.27

ENV GLIBC_227_64=/glibc/2.27/64
WORKDIR ${GLIBC_227_64}
RUN cp /tmp/libc6_2.27/lib/*/* .

# Compile the challenge binary
WORKDIR /src/challenge
COPY src src
COPY include include
COPY Makefile .
RUN make clean && make challenge

# Change challenge binary interpretor to libc 2.27
RUN patchelf --set-interpreter ${GLIBC_227_64}/ld-2.27.so challenge

COPY --from=registry.mlb.cromulence.com/has2/quals/generator-base/generator-base:latest /upload/ /upload

CMD [ "/bin/bash", "-c", "echo /src/challenge/challenge | /upload/upload.sh" ] 

# Thank you pedant
###
# Python Environment container
###

FROM ubuntu:20.04 AS python_env

RUN apt update ;\
    apt install -y --no-install-recommends \
        python3-venv \
        python3-dev \
        build-essential

ENV VIRTUAL_ENV="/opt/venv"
RUN /usr/bin/python3 -m venv --system-site-packages $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY requirements.txt /tmp/
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r /tmp/requirements.txt 


#######################
# Challenge container
#######################

FROM ubuntu:20.04
# FROM phusion/baseimage:master-amd64

ENV DEBIAN_FRONTEND noninteractive

RUN dpkg --add-architecture i386 && \
    apt-get -y update && \
    apt install -y \
    python3 tini

ENV GLIBC_227_64=/glibc/2.27/64

WORKDIR ${GLIBC_227_64}
COPY --from=builder ${GLIBC_227_64} ${GLIBC_227_64}

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
COPY --from=python_env /opt/venv /opt/venv


WORKDIR /challenge/
COPY --from=builder /src/challenge/challenge ./
COPY answer_index.txt ./
COPY src/startrack_sim.i2c ./
COPY src/player_voter.py ./
COPY src/voter_async.py ./
COPY run.sh ./

RUN groupadd -r --gid=1000 challenge && \
    useradd -m -r -s /bin/bash -g challenge --uid=1000 challenge && \
    mkdir -p /challenge && \
    chown -R challenge /challenge && \
    chgrp -R challenge /challenge 
USER challenge

RUN chmod +x ./challenge ./voter_async.py ./run.sh && \
    python -m compileall .

USER challenge
ENV PATH=$PATH:/challenge/.local/bin
CMD ["/usr/bin/tini", "--", "/challenge/run.sh"]