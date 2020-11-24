"""Generic menu actions."""

import logging

from telegram.error import BadRequest, TelegramError


def reply(update, context, text, buttons):
	if update.callback_query:
		try:
			update.callback_query.answer()
		except BadRequest as err:
			logging.warning("Query answer error - %s", err)
	message = update.effective_chat.send_message(text, reply_markup=buttons)
	if old_message := context.user_data.pop('old_message', None):
		try:
			old_message.delete()
		except BadRequest as err:
			logging.warning("Message delete error - %s", err)
	context.user_data['old_message'] = message


def start(update, context):
	context.user_data['current_menu'] = 'main'
	menus = context.bot_data['menu']
	update.effective_chat.send_message(menus['start']['message'])
	reply(update, context, menus['main']['message'], menus['main']['buttons'])


def back(update, context):
	current_menu_id = context.user_data.pop('current_menu')
	current_menu = context.bot_data['menu'].get(current_menu_id)
	previous_menu = context.bot_data['menu'].get(current_menu['back'])
	context.user_data['current_menu'] = current_menu['back']
	previous_menu = context.bot_data['menu']['main']
	reply(update, context, previous_menu['message'], previous_menu['buttons'])
	return -1


def choice(update, context):
	next_menu_id = int(update.callback_query.data)
	menu = context.bot_data['menu'][next_menu_id]
	context.user_data['current_menu'] = next_menu_id
	reply(update, context, menu['message'], menu['buttons'])


def clean(update, _context):
	update.effective_message.delete()


def error(update, context):
	if not update or not update.effective_user:
		logging.error("Ошибка - %s", context.error)
	else:
		try:
			update.effective_message.delete()
		except (AttributeError, TelegramError):
			pass
		user = update.effective_user.username or update.effective_user.id
		logging.warning("Сбой у пользователя '%s' - %s", user, context.error)
		start(update, context)
