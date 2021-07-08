FROM python:3.8-slim as builder

WORKDIR /solver

#COPY requirements.txt ./

#RUN pip install --no-cache-dir --upgrade pip && \
#    pip install --no-cache-dir -r requirements.txt

COPY solver.py /solver

CMD ["python", "solver.py"]
