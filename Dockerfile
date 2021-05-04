FROM python:3.9

WORKDIR /Q

COPY requirements.txt .

RUN apt update
RUN apt install -y build-essential python3.9 python3.9-dev
RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./main.py

CMD ["python", "main.py"]