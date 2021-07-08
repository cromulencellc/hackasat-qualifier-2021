FROM ubuntu:20.04 as builder

RUN apt update; \
    apt install -y g++ make


RUN apt update -y && \
    apt install -y gcc build-essential make python3

WORKDIR /src
ADD Makefile *.hpp *.cpp /src/

RUN make
COPY --from=registry.mlb.cromulence.com/has2/quals/generator-base/generator-base:latest /upload/ /upload

CMD ["/bin/bash", "-c", "echo /src/challenge | /upload/upload.sh"]


FROM ubuntu:20.04
RUN apt update; \
    apt-get install -y python3
WORKDIR /challenge
COPY --from=builder /src/challenge /challenge
CMD ["/challenge/challenge"]