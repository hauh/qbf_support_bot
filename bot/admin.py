"""Form for admin to upload a new version of menu."""

import logging
import os

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
	CallbackQueryHandler, CommandHandler,
	ConversationHandler, Filters, MessageHandler
)
from bot.excel import ParseError, parse_document
from bot.menu import back, reply

messages = {
	'admin': "Загрузите xlsx-файл с новым меню.",
	'fail': "Ошибка парсинга меню.",
	'success': "Меню обновлено."
}
back_btn = InlineKeyboardMarkup([
	[InlineKeyboardButton("Назад", callback_data='back')]
])


def admin(update, context):
	if update.effective_user.id != context.bot_data['admin']:
		update.effective_message.delete()
		return -1
	reply(update, context, messages['admin'], back_btn)
	return 1


def get_file(update, context):
	update.effective_chat.send_action(ChatAction.TYPING)
	file = update.effective_message.document.get_file()
	try:
		menu = parse_document(file.download())
	except ParseError as err:
		reply(update, context, messages['fail'] + "\n" + str(err), back_btn)
		return 1
	try:
		os.remove('menu.xlsx')
	except OSError:
		pass
	file.download(custom_path='./menu.xlsx')
	context.bot_data['menu'] = menu
	logging.info("Меню обновлено.")
	update.effective_message.reply_text(messages['success'], quote=True)
	return back(update, context)


admin_form = ConversationHandler(
	entry_points=[CommandHandler('admin', admin)],
	states={
		1: [MessageHandler(Filters.document, get_file)],
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
