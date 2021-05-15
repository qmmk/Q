FROM ubuntu:latest

RUN apt update
RUN apt-get update 
RUN apt-get install auditd -y
RUN apt-get install iptables sudo -y

RUN apt install -y build-essential python3 python3-dev

COPY . /project

RUN python3 project/get-pip.py
RUN python3 -m pip install -r project/requirements.txt

RUN rm project/get-pip.py

RUN chmod +x project/main.py

WORKDIR /project

ENTRYPOINT ["python3", "main.py"]
