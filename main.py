"""QBF Support Bot."""

import sys
import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from excel import parse_document, ParseError


FILENAME = 'sample.xlsx'


def main():
	try:
		menu = parse_document(FILENAME)
	except ParseError as err:
		print(f"Parse error in {err.args}")
		sys.exit(-1)

	updater = Updater(os.environ['TOKEN'])

	def answer(update, context, menu_id):
		if update.callback_query:
			update.callback_query.answer()
		context.user_data['current_menu'] = menu_id
		next_menu = menu.get(menu_id, menu['main'])
		update.effective_chat.send_message(
			text=next_menu['message'],
			reply_markup=next_menu['buttons']
		)

	def start(update, context):
		answer(update, context, 'main')

	def back(update, context):
		current_menu_id = context.user_data.get('current_menu', 'main')
		current_menu = menu.get(current_menu_id, menu['main'])
		answer(update, context, current_menu['back'])

	def next_menu(update, context):
		answer(update, context, int(update.callback_query.data))

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern=r'^back$'))
	updater.dispatcher.add_handler(CallbackQueryHandler(next_menu))

	updater.start_polling()
	updater.idle()


if __name__ == "__main__":
	main()
