FROM ubuntu:focal

WORKDIR /build
RUN apt update -y && \
    apt install -y gcc build-essential make python3
RUN apt install -y python3-pip && \
    pip3 install pwntools

COPY solver.py Makefile /build/
COPY src /build/src
ENV PWNLIB_NOTERM=true
ENV PART=1
RUN make

CMD python3 solver.py