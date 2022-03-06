FROM python:3-onbuild

# set a directory for the app
WORKDIR /usr/src/voice-client

# copy all the files to the container
COPY . .

RUN apt-get -y update
RUN apt-get install -y python3-pyaudio

# install dependencies
RUN pip install -r requirements.txt

# run the command
CMD ["python3", "./server-plus.py"]
