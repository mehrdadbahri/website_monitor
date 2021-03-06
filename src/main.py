import time
import sys
from datetime import datetime
import requests
import telegram
from pathlib import Path
from threading import Thread
import configparser
import logging_lib
import logging


class Monitor(object):
    running = True
    state = 'up'
    last_fail_time = None
    has_called = False
    fail_counter = 0

    def __init__(self):
        self.configs = configparser.ConfigParser()
        path = Path.home() / 'website_monitor.ini'
        self.configs.read(path)
        self.host = self.configs['Website']['url']
        self.title = self.configs['Website']['title']
        self.timeout = int(self.configs['main']['timeout'])
        self.sleep = int(self.configs['main']['sleep'])
        self.fail_counts = int(self.configs['main']['fails']) - 1
        self.fail_sleep = int(self.configs['main']['fail_sleep'])

    def start(self):
        session = requests.Session()
        while self.running:
            result = 'fail'
            try:
                response = session.get(self.host, timeout=self.timeout)
                if response.status_code == 200:
                    result = 'success'
            except requests.exceptions.RequestException as e:
                if self.configs['main']['log_errors'] == 'true':
                    logging_lib.log.logger.exception(e)
            if result == 'fail':
                self.fail_counter += 1
                if self.fail_counter > self.fail_counts:
                    self.website_down()
                    self.fail_counter = 0
            else:
                self.website_up()
                self.fail_counter = 0
            if self.fail_counter:
                time.sleep(self.fail_sleep)
            else:
                time.sleep(self.sleep)

    def website_up(self):
        if self.state == 'down':
            self.state = 'up'
            self.tg_alert()

    def website_down(self):
        if self.state == 'up':
            self.state = 'down'
            self.last_fail_time = datetime.now()
            self.tg_alert()
            return
        if not self.has_called:
            now = datetime.now()
            # it's been down for more than 10 minutes
            if (now - self.last_fail_time).total_seconds() > 600:
                self.call_alert()
                self.has_called = True

    def tg_alert(self):
        chat_ids = self.configs['Telegram']['accounts'].split(',')
        msg = self.get_alert_message()
        for chat_id in chat_ids:
            self.telegram_send(chat_id, msg)

    def telegram_send(self, chat_id, msg):
        bot_token = self.configs['Telegram']['token']
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id, msg, telegram.ParseMode.HTML)

    def get_alert_message(self):
        if self.state == 'down':
            return "??? Host {} is down.".format(self.title)
        return "??? Host {} is up".format(self.title)

    def call_alert(self):
        # TODO: implement alert with voice call
        pass


if __name__ == "__main__":
    # redirect stdout and stderr to log file
    sys.stderr = logging_lib.MyLogger(logging_lib.log.logger, logging.ERROR)
    sys.stdout = logging_lib.MyLogger(logging_lib.log.logger, logging.INFO)

    monitor = Monitor()
    discovery_thread = Thread(target=monitor.start, args=[])
    discovery_thread.daemon = True
    discovery_thread.start()

    while True:
        time.sleep(10)
