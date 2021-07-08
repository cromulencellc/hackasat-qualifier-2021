FROM python:3.8-slim as builder

WORKDIR /challenge

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ADD *.py /challenge/
# COPY challenge.py /challenge
COPY sats.tle spacejunk.tle /challenge/common/

CMD ["python3", "challenge.py"]
