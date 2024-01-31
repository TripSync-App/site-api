FROM python:slim

WORKDIR /project
RUN apt-get update && \
    apt-get install -y gcc

RUN python -m pip --no-cache-dir install pdm

COPY pyproject.toml pdm.lock /project/
COPY ./src/site_api/ /project/site_api

RUN pdm install --no-lock --no-editable -vv

EXPOSE 8000

ENTRYPOINT ["pdm", "run", "python", "-m", "uvicorn", "site_api.app:app", "--reload"]
