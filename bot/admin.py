"""Form for admin to upload a new version of menu."""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError, RetryAfter
from telegram.ext import (
	CallbackQueryHandler, CommandHandler,
	ConversationHandler, Filters, MessageHandler
)
from bot.excel import ParseError, parse_document
from bot.menu import back, reply

messages = {
	'admin': "Загрузите xlsx-файл с новым меню.",
	'fail': "Ошибка парсинга меню.",
	'test': "Тестируем сообщения...",
	'flood': "Слишком частые обновления. Попробуйте позже.",
	'success': "Меню обновлено!"
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
	file = update.effective_message.document.get_file()
	try:
		menu = parse_document(file.download())
	except ParseError as err:
		reply(update, context, messages['fail'] + "\n" + str(err), back_btn)
		return 1

	test_msg = update.effective_chat.send_message('Testing...')
	status_msg = update.effective_message.reply_text(messages['test'], quote=True)
	try:
		for submenu in menu.values():
			test_msg.edit_text(submenu['message'], reply_markup=submenu['buttons'])
	except RetryAfter as err:
		status_msg.edit_text(f"Ошибка Телеграма:\n{err}\n{messages['flood']}")
		reply(update, context, messages['fail'], back_btn)
		return 1
	except TelegramError as err:
		status_msg.edit_text(
			f"```{submenu['message']}```\nОшибка Телеграма:\n{err}\n"  # type: ignore
			"Скорее всего, в тексте неэкранированный спецсимвол, "
			"используемый для разметки."
		)
		reply(update, context, messages['fail'], back_btn)
		return 1
	finally:
		test_msg.delete()

	try:
		os.remove('menu.xlsx')
	except OSError:
		pass
	file.download(custom_path='./menu.xlsx')
	context.bot_data['menu'] = menu
	logging.info("Меню обновлено.")
	status_msg.edit_text(messages['success'])
	return back(update, context)


admin_form = ConversationHandler(
	entry_points=[CommandHandler('admin', admin)],
	states={
		1: [MessageHandler(Filters.document, get_file)],
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
