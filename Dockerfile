FROM python:3.8.6

MAINTAINER Viktor Andriichuk 'v.andriichuk@gmail.com'

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN apt-get install -y gunicorn

WORKDIR .
COPY . .


RUN pip install --upgrade pip
RUN pip install python-dotenv
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#RUN ["chmod", "+x", "./entrypoint.sh"]
#ENTRYPOINT ["./entrypoint.sh"]

#CMD flask run --host=0.0.0.0:5005

#CMD python runner.py db migrate -m  "Create DB" && python runner.py db upgrade && flask run --host=0.0.0.0:5005

#CMD flask run --host=0.0.0.0:5000

CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5005", "runner:app"]

