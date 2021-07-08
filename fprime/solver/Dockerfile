from registry.mlb.cromulence.com/has2/quals/challenges/fprime-exploitation/fprime-exploitation:challenge

USER root

RUN DEBIAN_FRONTEND="noninteractive" apt-get update && \
    DEBIAN_FRONTEND="noninteractive" apt-get  install  -y \
        python3 \
        binutils \ 
        wget \
        jq \
        sed \
        # firefox-esr \
        && apt-get clean autoclean \ 
        && rm -rf /var/lib/apt/lists/*


WORKDIR /home/ground/fprime/

# RUN pip install --upgrade --no-cache-dir \
#     selenium

# RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz
# RUN tar -xvzf geckodriver*
# RUN chmod +x geckodriver
# RUN mv geckodriver /usr/local/bin/


COPY solver.sh solver.py /home/ground/fprime/
RUN chmod +x /home/ground/fprime/solver.sh &&\ 
    chown ground /home/ground/*
USER ground

#ENTRYPOINT [ "/bin/bash", "./solver.sh"]

ENTRYPOINT [ "/home/ground/fprime/fprime-venv/bin/python3", "./solver.py" ]