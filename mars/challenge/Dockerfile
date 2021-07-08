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
    cp a.out.rom /usr/local/bin/bad.rom

FROM node:16

WORKDIR /app

RUN npm install ws express

COPY --from=builder /usr/local/bin/* ./
COPY src/simulator ./

RUN cp bad.rom html/bad.rom
EXPOSE 3000

CMD ["node", "app.js"]
