"""QBF Support Bot."""

import logging
import os
import sys

from telegram import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Defaults,
	Filters, MessageHandler, Updater
)

from bot import menu
from bot.admin import admin_form
from bot.contact import contact_form
from bot.excel import ParseError, parse_document


def main():
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
		updater = Updater(token, defaults=Defaults(
			parse_mode=ParseMode.MARKDOWN,
			disable_notification=True
		))
	except TelegramError as err:
		logging.critical("Ошибка подключения к телеграму - %s", err)
		sys.exit(1)

	try:
		menu_tree = parse_document('menu.xlsx')
	except ParseError as err:
		logging.error("Ошибка парсинга файла - %s", err)
		menu_tree = {'main': {'message': "Ошибка загрузки меню.", 'buttons': None}}

	dispatcher = updater.dispatcher
	dispatcher.bot_data['admin'] = admin
	dispatcher.bot_data['menu'] = menu_tree

	dispatcher.add_handler(CommandHandler('start', menu.start))
	dispatcher.add_handler(admin_form)
	dispatcher.add_handler(contact_form)
	dispatcher.add_handler(CallbackQueryHandler(menu.back, pattern=r'^back$'))
	dispatcher.add_handler(CallbackQueryHandler(menu.choice))
	dispatcher.add_handler(MessageHandler(Filters.all, menu.clean))

	dispatcher.add_error_handler(menu.error)

	updater.start_polling()
	logging.info("Бот запущен!")
	updater.idle()
	logging.info("Бот выключен.")


if __name__ == "__main__":
	main()
