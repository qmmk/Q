FROM debian:latest
COPY . /Q

RUN apt update
RUN apt install -y build-essential python3.9 python3.9-dev
RUN chmod +x /Q/main.py

CMD ["python3", "main.py"]