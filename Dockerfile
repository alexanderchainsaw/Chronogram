FROM python:3.11-slim

#RUN apt-get update
#RUN apt-get install python3 python3-pip -y
#RUN pip3 install --upgrade pip
WORKDIR /Chronogram

RUN pip install poetry
#COPY ./requirements.txt /Chronogram/requirements.txt

#RUN pip3 install -r requirements.txt
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev

COPY . .

CMD poetry run python __main__.py