FROM python:3.8-buster

RUN pip install pipenv

RUN mkdir code

WORKDIR code

COPY Pipfile .

COPY Pipfile.lock .

COPY run.py .

RUN pipenv install

EXPOSE 5000

ENTRYPOINT cd server && pipenv run flask db upgrade && \
           cd .. && pipenv run python run.py