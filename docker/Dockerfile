FROM debian:bookworm-slim

#Create app directory
RUN apt update && apt install -y python3 python3-pip wireguard
RUN mkdir /app
WORKDIR /app

# Install dependencies
COPY ../* ./
RUN pip install -r requirements.txt --break-system-packages

CMD "python3" "app.py"