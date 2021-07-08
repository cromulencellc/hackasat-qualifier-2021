FROM python:3.7-slim-buster AS python_env

WORKDIR /src
RUN apt update && \
    apt install -y --no-install-recommends \
            python3-dev \
            python3-venv \
            build-essential
    
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"
RUN /usr/local/bin/python3 -m venv --system-site-packages $VIRTUAL_ENV

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install numpy pwntools
    
FROM python:3.7-slim-buster

COPY --from=python_env /opt/venv /opt/venv

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

ARG WORKDIR=/solver
WORKDIR ${WORKDIR}

ARG UID=1000
ARG GID=1000
ARG USER=solver
ARG GROUP=${USER}

RUN groupadd -r --gid=${GID} ${GROUP} && \
    useradd -r -s /bin/false --uid=${UID} -g ${GROUP} ${USER} && \
    chown -R ${USER}:${GROUP} ${WORKDIR}

USER ${USER}

COPY *.py ${WORKDIR}/
RUN python3 -m compileall . -q 

ENV PWLLIB_NOTERM=true

CMD python solver.py
