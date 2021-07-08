FROM ubuntu:18.04 as fprime-builder

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
    groupadd -g ${GID} $USERNAME &&\
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

# ENTRYPOINT ["/bin/bash"]

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

# USER has

# ENV BUILD_DIR=/home/has/fprime

# ENV VIRTUAL_ENV=${BUILD_DIR}/fprime-venv

# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --chown=has:has ./QualsRef ${BUILD_DIR}/QualsRef

WORKDIR ${BUILD_DIR}/QualsRef/

RUN ./build.sh

from debian:buster-slim as fprime-challenge

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get  install  -y \
        python3 \
        python3-pip \
        python3-venv \
        && apt-get clean autoclean \ 
        && rm -rf /var/lib/apt/lists/*

ARG SPACE_UID=1000
ARG SPACE_GID=1000
ARG SPACE_USERNAME=space

ARG BUILD_EXE_DIR=/home/has/fprime

ENV SPACE_DIR=/home/${SPACE_USERNAME}/fprime

RUN if [ ${SPACE_UID:-0} -ne 0 ] && [ ${SPACE_GID:-0} -ne 0 ]; then \
    groupadd -g ${SPACE_GID} $SPACE_USERNAME &&\
    useradd -l -m -u ${SPACE_UID} -g $SPACE_USERNAME $SPACE_USERNAME; \
    fi 

RUN chmod -R o-rwx /home/${SPACE_USERNAME}

# USER ${SPACE_USERNAME}

# RUN mkdir /working
# RUN mkdir -p ${BUILD_DIR} && mkdir -p /home/${USERNAME}/secure

# COPY ./rpi/2021-03-04-raspios-buster-armhf-lite.img /working/2021-03-04-raspios-buster-armhf-lite.img

COPY --chown=${SPACE_USERNAME}:${SPACE_USERNAME} --from=fprime-builder ${BUILD_EXE_DIR}/QualsRef/build-artifacts/Linux/bin/QualsRef ${SPACE_DIR}/satellite.exe

RUN chmod u+x ${SPACE_DIR}/satellite.exe

RUN strip -s ${SPACE_DIR}/satellite.exe

# COPY --from=fprime-builder ${BUILD_DIR}/QualsRef/FlagData.txt /home/has/secure/.FlagData

# COPY ./update_rpi_image.sh /update_rpi_image.sh 

# RUN /bin/bash /update_rpi_image.sh /working/2021-03-04-raspios-buster-armhf-lite.img /working/QualsRef /working/FlagData.txt

# WORKDIR ${BUILD_DIR}

# USER root

ARG GROUND_UID=1001
ARG GROUND_GID=1001
ARG GROUND_USERNAME=ground

ENV GROUND_DIR=/home/${GROUND_USERNAME}/fprime

RUN if [ ${GROUND_UID:-0} -ne 0 ] && [ ${GROUND_GID:-0} -ne 0 ]; then \
    groupadd -g ${GROUND_GID} $GROUND_USERNAME &&\
    useradd -l -m -u ${GROUND_UID} -g $GROUND_USERNAME $GROUND_USERNAME; \
    fi 

RUN chmod -R o-rwx /home/${GROUND_USERNAME}

USER ${GROUND_USERNAME}

# ENTRYPOINT ["./satellite.exe", "-a", "172.16.238.3", "-p",  "50000"]
# # Build Ground Based on Slim Debian 
# from debian:buster-slim as fprime-ground

RUN mkdir -p ${GROUND_DIR}

WORKDIR ${GROUND_DIR}

ENV VIRTUAL_ENV=${GROUND_DIR}/fprime-venv

RUN python3 -m venv ${VIRTUAL_ENV}

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY --from=fprime-builder ${BUILD_EXE_DIR}/fprime ${GROUND_DIR}/fprime

WORKDIR ${GROUND_DIR}/fprime/

RUN pip install --upgrade --no-cache-dir \
    wheel \
    setuptools \
    pip \ 
    fprime-tools \
    fprime-gds

COPY --from=fprime-builder ${BUILD_EXE_DIR}/QualsRef/build-artifacts/Linux/dict/RefTopologyAppDictionary.xml ${GROUND_DIR}/dict/RefTopologyAppDictionary.xml

USER root

WORKDIR /

COPY ./run.sh /run.sh

COPY ./run_ground.sh /run_ground.sh

COPY ./run_space.sh /run_space.sh

ENTRYPOINT [ "/bin/bash", "./run.sh" ]