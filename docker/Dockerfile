FROM python:alpine

#Create app directory
RUN mkdir /app
WORKDIR /app

# Install dependencies
COPY ./source ./
RUN pip install -r requirements.txt

CMD "python3" "app.py"