FROM python:3.9

COPY requirements.txt /opt/ls_bot/requirements.txt
WORKDIR /opt/ls_bot
RUN pip install -r requirements.txt
COPY . .

CMD ["python", "./bot.py"]

