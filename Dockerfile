FROM python:3.5-alpine3.9
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
ADD ./run.py ./
CMD [ "python", "./run.py" ]