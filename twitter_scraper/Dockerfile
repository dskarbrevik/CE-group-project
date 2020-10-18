FROM python:3.8

RUN apt-get update
RUN apt-get install g++

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code

CMD ["python","/code/twitter_scrape.py"]
