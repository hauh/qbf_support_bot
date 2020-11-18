"""QBF Support Bot."""

import sys
import os
import logging

from telegram import TelegramError
from telegram.ext import (
	Updater, Filters, CommandHandler, MessageHandler, CallbackQueryHandler)

from excel import parse_document, ParseError
from contact import contact_form


FILENAME = 'menu.xlsx'


def answer(update, context, menu_id):
	if update.callback_query:
		update.callback_query.answer()
	context.user_data['current_menu'] = menu_id
	next_menu = context.bot_data['menu'].get(menu_id)
	message_kwargs = {
		'text': next_menu['message'],
		'reply_markup': next_menu['buttons'],
		'parse_mode': 'Markdown'
	}
	if message := context.user_data.pop('last_message', None):
		message.edit_text(**message_kwargs)
	else:
		message = update.effective_chat.send_message(**message_kwargs)
	context.user_data['last_message'] = message


def start(update, context):
	if last_message := context.user_data.pop('last_message', None):
		last_message.delete()
	update.effective_chat.send_message(text=context.bot_data['menu']['start'])
	answer(update, context, 'main')


def back(update, context):
	menu_id = context.user_data.get('current_menu', 'main')
	menu = context.bot_data['menu'].get(menu_id, context.bot_data['menu']['main'])
	answer(update, context, menu['back'])


def choice(update, context):
	answer(update, context, int(update.callback_query.data))


def clean(update, _context):
	update.effective_message.delete()


def error(update, context):
	user = update.effective_user.username or update.effective_user.id
	logging.warning("Ошибка у пользователя '%s' - %s", user, context.error)
	answer(update, context, 'main')


def main():
	logging.basicConfig(
		level=logging.INFO,
		format="%(asctime)s - %(levelname)s - %(module)s - %(message)s",
		handlers=[
			logging.FileHandler('bot.log', 'a', 'utf-8'),
			logging.StreamHandler()
		],
		force=True
	)

	try:
		token = os.environ['TOKEN']
	except KeyError:
		logging.critical("Токен бота ('TOKEN') не найден в переменных окружения!")
		sys.exit(1)

	try:
		admin = os.environ['ADMIN']
	except KeyError:
		logging.critical("Ник админа ('ADMIN') не найден в переменных окружения!")
		sys.exit(1)

	try:
		menu = parse_document(FILENAME)
	except ParseError as err:
		logging.critical("Ошибка парсинга файла - %s", err)
		sys.exit(1)

	try:
		updater = Updater(token)
	except TelegramError as err:
		logging.critical("Ошибка подключения к телеграму - %s", err)
		sys.exit(1)

	logging.info("Бот запущен!")

	updater.dispatcher.bot_data['admin'] = admin
	updater.dispatcher.bot_data['menu'] = menu

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(contact_form)
	updater.dispatcher.add_handler(MessageHandler(Filters.all, clean))
	updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern=r'^back$'))
	updater.dispatcher.add_handler(CallbackQueryHandler(choice))

	updater.dispatcher.add_error_handler(error)

	updater.start_polling()
	updater.idle()

	logging.info("Бот выключен.")


if __name__ == "__main__":
	main()
