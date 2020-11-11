"""QBF Support Bot."""

import sys
import os
from telegram import TelegramError
from telegram.ext import (
	Updater, Filters, CommandHandler, MessageHandler, CallbackQueryHandler)
from excel import parse_document, ParseError
from contact import contact_form


FILENAME = 'menu.xlsx'


def answer(update, context, menu_id):
	context.user_data['current_menu'] = menu_id
	next_menu = context.bot_data['menu'].get(menu_id)
	if update.callback_query:
		update.callback_query.answer()
	if last_message := context.user_data.pop('last_message', None):
		last_message.edit_text(next_menu['message'])
		last_message.edit_reply_markup(reply_markup=next_menu['buttons'])
	else:
		message = update.effective_chat.send_message(
			text=next_menu['message'],
			reply_markup=next_menu['buttons']
		)
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
	answer(update, context, 'main')


def main():
	updater = None
	menu = None

	try:
		updater = Updater(os.environ['TOKEN'])
	except KeyError:
		print("Токен бота не указан в переменных окружения!")
	except TelegramError as err:
		print(f"Ошибка подключения к телеграму: {err.args}")

	try:
		menu = parse_document(FILENAME)
	except ParseError as err:
		print(f"Ошибка парсинга файла {err.args}")

	if not updater or not menu:
		sys.exit(-1)

	updater.dispatcher.bot_data['menu'] = menu

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(contact_form)
	updater.dispatcher.add_handler(MessageHandler(Filters.all, clean))
	updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern=r'^back$'))
	updater.dispatcher.add_handler(CallbackQueryHandler(choice))

	updater.dispatcher.add_error_handler(error)

	updater.start_polling()
	updater.idle()


if __name__ == "__main__":
	main()
