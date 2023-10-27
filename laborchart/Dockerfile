FROM python:3.10-slim

WORKDIR /usr/src/app

RUN mkdir Dagster

ENV DAGSTER_HOME=/usr/src/app/Dagster

COPY requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

COPY dataflow.py .
COPY etl ./etl
COPY pyproject.toml .
COPY setup.py .
COPY setup.cfg .

EXPOSE 3000

CMD ["dagster", "dev", "-f", "dataflow.py", "-h", "0.0.0.0", "-p", "3000"]