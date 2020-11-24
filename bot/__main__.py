"""QBF Support Bot."""

import logging
import os
import sys

from telegram.error import TelegramError

from bot.excel import ParseError, parse_document
from bot.run import run

if __name__ == "__main__":

	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
	)

	try:
		token = os.environ['TOKEN']
	except KeyError:
		logging.critical("Токен бота ('TOKEN') не найден в переменных окружения!")
		sys.exit(1)

	try:
		admin = int(os.environ['ADMIN'])
	except KeyError:
		logging.critical("ID админа ('ADMIN') не найден в переменных окружения!")
		sys.exit(1)
	except ValueError:
		logging.critical("ID админа должен быть числом!")
		sys.exit(1)

	try:
		menu = parse_document('menu.xlsx')
	except ParseError as err:
		logging.critical("Ошибка парсинга файла - %s", err)
		sys.exit(1)

	try:
		run(token, admin, menu)
	except TelegramError as err:
		logging.critical("Ошибка подключения к телеграму - %s", err)
		sys.exit(1)
