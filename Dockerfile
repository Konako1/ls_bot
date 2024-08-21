FROM python:3.9

COPY requirements.txt /opt/ls_bot/requirements.txt
WORKDIR /opt/ls_bot
RUN pip install -r requirements.txt
COPY . .


#fix issues with aiogram lib
COPY ./aiogram /usr/local/lib/python3.9/site-packages

CMD ["python", "./bot.py"]

