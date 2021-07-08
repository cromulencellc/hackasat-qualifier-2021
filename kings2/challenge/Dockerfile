FROM ubuntu:20.04 AS base

RUN apt update -y && \
    apt install -y openssl && \
    apt -y autoclean

FROM ubuntu:20.04 AS builder

WORKDIR /build
RUN apt update -y && \
    apt install -y gcc build-essential make python3
RUN apt install -y python3-pip && \
    pip3 install pwntools

COPY Makefile /build/
COPY src /build/src
COPY include /build/include
ENV PWNLIB_NOTERM=true
RUN make

FROM base
WORKDIR /challenge
COPY --from=builder /build/challenge /build/exploit.bin /build/runner /challenge/
RUN groupadd -r --gid=1000 challenge && \
    useradd -m -r -s /bin/bash -g challenge --uid=1000 challenge && \
    mkdir -p /challenge && \
    chown -R challenge /challenge && \
    chgrp -R challenge /challenge 
USER challenge
COPY entrypoint.sh /
ENV SERVICE_HOST=localhost
ENV SERVICE_PORT=54321
ENTRYPOINT [ "/entrypoint.sh" ]