FROM python:3.7-slim AS python_env

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"

RUN python -m venv $VIRTUAL_ENV ;\
    pip install --upgrade pip ;\
    pip install --no-cache-dir numpy matplotlib

FROM python:3.7-slim

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="/opt/venv/bin:$PATH"
COPY --from=python_env /opt/venv /opt/venv

WORKDIR /solver
ADD solve.py /solver

CMD ["python", "solve.py"]
