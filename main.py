"""QBF Support Bot."""

import sys
import os
from telegram.ext import (
	Updater, Filters, CommandHandler, MessageHandler, CallbackQueryHandler)
from excel import parse_document, ParseError
from contact import contact_form


FILENAME = 'sample2.xlsx'


def answer(update, context, menu_id):
	context.user_data['current_menu'] = menu_id
	next_menu = context.bot_data['menu'].get(menu_id)
	if last_message := context.user_data.get('last_message'):
		last_message.edit_text(next_menu['message'])
		last_message.edit_reply_markup(reply_markup=next_menu['buttons'])
	else:
		if update.callback_query:
			update.callback_query.answer()
		message = update.effective_chat.send_message(
			text=next_menu['message'],
			reply_markup=next_menu['buttons']
		)
		context.user_data['last_message'] = message


def start(update, context):
	answer(update, context, 'main')


def back(update, context):
	current_menu_id = context.user_data.get('current_menu', 'main')
	current_menu = context.bot_data['menu'].get(current_menu_id)
	answer(update, context, current_menu['back'])


def choice(update, context):
	answer(update, context, int(update.callback_query.data))


def clean(update, _context):
	update.effective_message.delete()


def main():
	updater = Updater(os.environ['TOKEN'])

	try:
		updater.dispatcher.bot_data['menu'] = parse_document(FILENAME)
	except ParseError as err:
		print(f"Parse error in {err.args}")
		sys.exit(-1)

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(contact_form)
	updater.dispatcher.add_handler(MessageHandler(Filters.all, clean))
	updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern=r'^back$'))
	updater.dispatcher.add_handler(CallbackQueryHandler(choice))

	updater.dispatcher.add_error_handler(start)

	updater.start_polling()
	updater.idle()


if __name__ == "__main__":
	main()
