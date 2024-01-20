FROM python:slim

WORKDIR /project
RUN python -m pip --no-cache-dir install pdm

COPY pyproject.toml pdm.lock /project/
COPY ./src/site_api/ /project/site_api

RUN pdm install --prod --no-lock --no-editable -vv

EXPOSE 5000

ENTRYPOINT ["pdm", "run", "python", "-m", "uvicorn", "site_api.app:app"]
