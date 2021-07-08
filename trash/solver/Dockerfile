FROM python:3.8-slim

WORKDIR /solver

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ADD solver.py /solver
COPY sats.tle spacejunk.tle /solver/common/

CMD ["python", "solver.py"]
