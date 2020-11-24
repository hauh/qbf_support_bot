"""New menu upload for admin."""

import logging
import os

from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler

from bot.excel import ParseError, parse_document
from bot.form import form_action, form_conversation


messages = {
	'admin': "Загрузите xlsx-файл с новым меню.",
	'fail': "Ошибка парсинга меню.",
	'success': "Меню обновлено."
}
back_btn = InlineKeyboardMarkup([
	[InlineKeyboardButton("Назад", callback_data='back')]
])


@form_action
def admin(update, context):
	if update.effective_user.id != context.bot_data['admin']:
		return_menu = context.bot_data['menu']['main']
		return -1, return_menu['message'], return_menu['buttons']
	return 1, messages['admin'], back_btn


@form_action
def get_file(update, context):
	update.effective_chat.send_action(ChatAction.TYPING)
	file = update.effective_message.document.get_file()
	try:
		menu = parse_document(file.download())
	except ParseError as err:
		return 1, messages['fail'] + "\n" + str(err), back_btn
	try:
		os.remove('menu.xlsx')
	except OSError:
		pass
	file.download(custom_path='./menu.xlsx')
	context.bot_data['menu'] = menu
	logging.info("Меню обновлено.")
	update.effective_message.reply_text(messages['success'], quote=True)
	return -1, menu['main']['message'], menu['main']['buttons']


admin_form = form_conversation(
	entry_points=[CommandHandler('admin', admin)],
	states={
		1: [MessageHandler(Filters.document, get_file)],
	},
)
