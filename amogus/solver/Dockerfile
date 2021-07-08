FROM ubuntu:focal

WORKDIR /build
RUN apt update -y && \
    apt install -y gcc build-essential make python3
RUN apt install -y python3-pip && \
    pip3 install pwntools construct 

COPY solver.py /solve/
ENV PWNLIB_NOTERM=true

WORKDIR /solve

RUN chmod +x solver.py 
CMD python3 solver.py