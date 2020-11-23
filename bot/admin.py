"""New menu upload for admin."""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler, ChatActions

from bot.excel import parse_document, ParseError
from bot.form import form_action, form_conversation


messages = {
	'admin': "Загрузите xlsx-файл с новым меню.",
	'confirm': "Новое меню сгенерировано. Обновить?",
	'fail': "Ошибка парсинга меню.",
	'success': "Меню обновлено!"
}
back_btn = InlineKeyboardMarkup([
	[InlineKeyboardButton("Назад", callback_data='back')]
])


@form_action
def admin(update, context):
	return 1, form['admin'], back_btn


@form_action
def get_file(update, context):
	update.effective_chat.send_action(ChatActions.TYPING)
	file = update.effective_attachment.get_file()
	try:
		menu = parse_document(file)
	except ParseError as err:
		return 1, form['fail'] + "\n" + str(err), back_btn
	try:
		os.remove('menu.xlsx')
	except OSError:
		pass
	file.download(custom_path='./menu.xlsx')
	context.bot_data['menu'] = menu
	logging.info("Меню обновлено.")
	return -1, menu['main']['message'], menu['main']['buttons']


admin_form = form_action(
	entry_points=[CallbackQueryHandler(admin, pattern=r'^admin$')],
	states={
		1: [MessageHandler(Filters.document, get_file)],
	},
)
