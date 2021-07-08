FROM ubuntu:18.04 as fprime-base

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Etc/UTC

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get  install  -y \
        # cmake \
        curl \
        # default-jre \
        # libssl-dev \
        # libyaml-dev \
        # libffi-dev \
        # libreadline6-dev \
        # zlib1g-dev \
        # python-dev \
        # xxd \
        # gcc-arm-linux-gnueabihf \
        # g++-arm-linux-gnueabihf \
        build-essential \
        cmake \
        python3 \
        python3-pip \
        python3-venv \
        git \
        && apt-get clean autoclean \ 
        && rm -rf /var/lib/apt/lists/*

ARG UID=1000
ARG GID=1000
ARG USERNAME=has

RUN if [ ${UID:-0} -ne 0 ] && [ ${GID:-0} -ne 0 ]; then \
    groupadd -g ${UID} $USERNAME &&\
    useradd -l -m -u ${UID} -g $USERNAME $USERNAME; \
    fi 

    # && \
    # apt-get install -y sudo \
    # && echo  ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    # && chmod 0440 /etc/sudoers.d/$USERNAME

# RUN mkdir -p /opt/rpi/tools/arm-bcm2708
# WORKDIR /opt/rpi/tools/arm-bcm2708

# RUN curl https://codeload.github.com/raspberrypi/tools/tar.gz/master | tar -xz --strip=2 tools-master/arm-bcm2708

USER $USERNAME

ENV BUILD_DIR=/home/${USERNAME}/fprime

RUN mkdir -p ${BUILD_DIR}

RUN chown -R ${USERNAME}:${USERNAME} ${BUILD_DIR}

WORKDIR ${BUILD_DIR}

ENTRYPOINT ["/bin/bash"]

RUN git clone https://github.com/nasa/fprime.git && \
    cd fprime && \
    git checkout d32dfa9ceedbc046db45b451c56de7f1f9196348

# COPY ./raspberrypi-toolchain.patch /working/

# RUN git --git-dir=/working/fprime apply raspberrypi-toolchain.patch

ENV VIRTUAL_ENV=${BUILD_DIR}/fprime-venv

RUN python3 -m venv ${VIRTUAL_ENV}

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR ${BUILD_DIR}/fprime/

RUN pip install --upgrade --no-cache-dir \
    wheel \
    setuptools \
    pip \
    fprime-tools \
    fprime-gds

# COPY ./raspberrypi-toolchain.patch /working/fprime/raspberrypi-toolchain.patch