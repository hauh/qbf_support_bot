"""Bot runs here."""

import logging

from telegram import Bot, ParseMode
from telegram.error import BadRequest
from telegram.ext import (
	CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater)
from telegram.utils.request import Request

from bot.contact import contact_form
from bot.admin import admin_form


class SafeRequestsBot(Bot):
	"""Ignores failed requests."""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs, request=Request(con_pool_size=10))

	@staticmethod
	def safe_request(method, *args, **kwargs):
		try:
			return method(*args, **kwargs)
		except BadRequest as err:
			logging.warning("Bot error - %s", err)
			return False

	def answer_callback_query(self, *args, **kwargs):
		return self.safe_request(super().answer_callback_query, *args, **kwargs)

	def delete_message(self, *args, **kwargs):
		return self.safe_request(super().delete_message, *args, **kwargs)

	def edit_message_text(self, *args, **kwargs):
		return self.safe_request(super().edit_message_text, *args, **kwargs)


def answer(update, context, menu_id):
	if next_menu := context.bot_data['menu'].get(menu_id):
		if update.callback_query:
			update.callback_query.answer()
		context.user_data['current_menu'] = menu_id
		message_kwargs = {
			'text': next_menu['message'],
			'reply_markup': next_menu['buttons'],
			'parse_mode': ParseMode.MARKDOWN
		}
		if message := context.user_data.pop('last_message', None):
			message.edit_text(**message_kwargs)
		else:
			message = update.effective_chat.send_message(**message_kwargs)
		context.user_data['last_message'] = message
	else:
		if update.callback_query and update.callback_query.message:
			update.callback_query.message.delete()
		answer(update, context, 'main')


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
	if not update or not update.effective_user:
		logging.error("Ошибка - %s", context.error)
	else:
		user = update.effective_user.username or update.effective_user.id
		logging.warning("Сбой у пользователя '%s' - %s", user, context.error)
		answer(update, context, 'main')


def run(token, admin, menu):
	updater = Updater(bot=SafeRequestsBot(token))

	updater.dispatcher.bot_data['admin'] = admin
	updater.dispatcher.bot_data['menu'] = menu

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(admin_form)
	updater.dispatcher.add_handler(contact_form)
	updater.dispatcher.add_handler(MessageHandler(Filters.all, clean))
	updater.dispatcher.add_handler(CallbackQueryHandler(back, pattern=r'^back$'))
	updater.dispatcher.add_handler(CallbackQueryHandler(choice))

	updater.dispatcher.add_error_handler(error)

	updater.start_polling()
	logging.info("Бот запущен!")
	updater.idle()
	logging.info("Бот выключен.")
