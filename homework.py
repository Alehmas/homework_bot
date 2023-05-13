import json
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIValueException

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'The work is checked: the reviewer liked everything.',
    'reviewing': 'The work was taken for verification by the reviewer.',
    'rejected': 'The work has been checked: the reviewer has comments.'
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main.log',
    filemode='a',
    format='%(asctime)s  [%(levelname)s]  %(message)s'
)
logger = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  [%(levelname)s]  %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


def send_message(bot, message):
    """Sends a message to the bot."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(message)
    except telegram.error.TelegramError:
        logger.error('Problems sending messages to Telegram')


def get_api_answer(current_timestamp):
    """Makes a request to an API service."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise APIValueException(
                f'API not available: error {response.status_code}')
        return response.json()
    except json.JSONDecodeError:
        raise APIValueException(
            'Problem with converting from JSON API response')
    except requests.ConnectionError:
        raise ConnectionError('Server is not available')


def check_response(response):
    """Checks the API response for correctness."""
    if not isinstance(response, dict):
        raise TypeError('Received response is not a dictionary')
    if 'homeworks' not in response:
        raise KeyError('No homeworks key')
    if not isinstance(response['homeworks'], list):
        raise TypeError('There is no list in the answer.')
    return response.get('homeworks')


def parse_status(homework):
    """Processes received homework."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
    elif homework_name is None:
        raise KeyError('Missing homework_status key')
    elif homework_status is None:
        raise KeyError('Missing key homework_name')
    else:
        raise KeyError('Unexpected Status')
    logger.info('Homework status change received')
    return f'Job verification status changed "{homework_name}". {verdict}'


def check_tokens():
    """Checking environment variables."""
    tokens = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    counter = 0
    for name in tokens:
        token = globals()[name]
        if not token:
            counter += 1
            logger.critical(f'Missing variable {name}')
    if counter > 0:
        return False
    logger.info('All environment variables received')
    return True


def main():
    """The main logic of the bot."""
    if not check_tokens():
        return
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework_date = check_response(response)
            if len(homework_date) == 0:
                logger.debug('Homework status has not changed')
            else:
                message = parse_status(homework_date[0])
                send_message(bot, message)
                current_timestamp = response.get('current_date')
            old_message = ''
        except Exception as error:
            message = f'Program crash: {error}'
            logger.error(message)
            if old_message != message:
                send_message(bot, message)
                old_message = message
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
