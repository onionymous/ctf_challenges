FROM python:3.12-slim

RUN apt update && apt install -y sqlite3

WORKDIR /app
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt --no-cache-dir

ADD templates /app/templates
ADD main.py /app/main.py
ADD static /app/static
ADD database_setup.sql /app/database_setup.sql
ADD launch.sh /app/launch.sh

CMD ["./launch.sh"]
