FROM python:3.8-slim as builder

WORKDIR /challenge

# COPY requirements.txt ./

#RUN pip install --no-cache-dir --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt

# COPY challenge.py /challenge

ADD timeout.py challenge.py /challenge/

CMD ["python", "challenge.py"]
