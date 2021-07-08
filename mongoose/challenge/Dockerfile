FROM ubuntu:20.04 AS builder

RUN apt -y update && \
    apt -y install --no-install-recommends \
        build-essential \
        gcc-mipsel-linux-gnu \
        g++-mipsel-linux-gnu \
        binutils-mipsel-linux-gnu \
        libc6-dev

WORKDIR /vmips
ADD src/vmips /vmips/
RUN ./configure && \
    make && \
    make install

WORKDIR /controller
ADD src/controller /controller/
RUN make && \
    make rom && \
    cp a.out.rom /usr/local/bin/firmware.rom

FROM ubuntu:20.04

WORKDIR /challenge

COPY --from=builder /usr/local/bin/* ./

CMD ["./vmips", "-o", "fpu", "-o", "memsize=3000000", "firmware.rom"]
