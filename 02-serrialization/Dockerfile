FROM python:3-onbuild

# set a directory for the app
WORKDIR /usr/src/bench

# copy all the files to the container
COPY . .

# install dependencies
RUN pip install -r requirements.txt

# somehow it works like this but not from requirements o_O
RUN easy_install pyyaml

# run the command
CMD ["python", "./benchmark.py"]
