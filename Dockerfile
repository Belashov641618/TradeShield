FROM python:3.12
RUN apt-get update && apt-get install -y python3-pip libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /home/
RUN pip3 install --no-cache-dir -r /home/requirements.txt

WORKDIR /home
