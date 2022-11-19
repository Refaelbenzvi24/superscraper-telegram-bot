FROM python:3.10 AS builder


RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /app/

WORKDIR /app
RUN mkdir __pypackages__ && pdm install --prod --no-lock --no-editable


FROM python:3.10


ENV PYTHONPATH=/app/pkgs
COPY --from=builder /app/__pypackages__/3.10/lib /app/pkgs

COPY src/celery /app/src/celery
COPY src/shared app/src/shared
COPY src/config app/src/config

WORKDIR /app

CMD ["python", "-m", "src.celery.worker"]