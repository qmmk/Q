FROM debian:latest

WORKDIR /Q

COPY . .

RUN apt-get update && apt-get -y install build-essential python3-pip python3.7-dev
RUN pip3 install -r requirements.txt

CMD ["/bin/bash"]
