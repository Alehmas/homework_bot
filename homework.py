import datetime as dt
import json
import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIValueException, EmptyDictException

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 60
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
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
    """Отправляет сообщение в бот."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(message)
    except telegram.error.TelegramError:
        logger.error('Проблемы отправки сообщений в Telegram')


def get_api_answer(current_timestamp):
    """Делает запрос к API-сервисау."""
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != 200:
            raise APIValueException
        return response.json()
    except APIValueException:
        message = f'API недоступен: ошибка {response.status_code}'
        logger.error(message)
        raise APIValueException(message)
    except json.JSONDecodeError:
        message = 'Проблема с конвертацией из JSON ответа API'
        logger.error(message)
        raise Exception(message)


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        message = 'Полученный ответ не словарь'
        logger.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'Нет ключа homeworks'
        logger.error(message)
        raise KeyError(message)
    if not isinstance(response['homeworks'], list):
        message = 'В ответе нет списка'
        logger.error(message)
        raise TypeError(message)
    return response.get('homeworks')


def parse_status(homework):
    """Обрабатывает полученную домашнюю работу."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES[homework_status]
    elif homework_status is None:
        logger.error('Отсутствует ключ homework_status')
        raise KeyError('Отсутствует ключ homework_status')
    else:
        logger.error('Неожиданный статус')
        raise KeyError('Неожиданный статус')
    logger.info('Измение статуса домашнего задания получено')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка переменных окружения."""
    tokens = ['PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID']
    for name in tokens:
        token = globals()[name]
        if token is None or token == '':
            logger.critical(f'Не хватает переменной {name}')
            return False
    logger.info('Все переменные окружения получены')
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        return logger.critical('Программа принудительно остановлена.')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    old_message = ''

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework_date = check_response(response)
            if len(homework_date) == 0:
                raise EmptyDictException
            upd_time = dt.datetime.strptime(
                homework_date[0].get('date_updated'),
                '%Y-%m-%dT%H:%M:%SZ'
            )
            upd_time_unix = time.mktime(upd_time.timetuple())
            if upd_time_unix > current_timestamp:
                message = parse_status(homework_date[0])
                send_message(bot, message)
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except EmptyDictException:
            logger.debug('Статус домашней работы не изменился')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if old_message != message:
                send_message(bot, message)
                old_message = message
            time.sleep(RETRY_TIME)
        else:
            ...


if __name__ == '__main__':
    main()
