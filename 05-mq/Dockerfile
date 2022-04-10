FROM python:3-onbuild

# set a directory for the app
WORKDIR /usr/src/mq-client

# copy all the files to the container
COPY . .

RUN apt-get -y update

# install dependencies
RUN pip install -r requirements.txt

# run the command
CMD ["python3", "./server.py"]