FROM python:3.8-slim as python_env
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./

RUN python -m venv $VIRTUAL_ENV ;\
    pip install --upgrade pip ;\
    pip install --no-cache-dir -r requirements.txt

FROM python:3.8-slim
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=python_env /opt/venv /opt/venv

WORKDIR /challenge

COPY *.py /challenge/

CMD ["python", "challenge.py"]
