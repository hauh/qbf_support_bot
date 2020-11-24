"""Contact customer form."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler

from bot.form import form_action, form_conversation

messages = {
	'name': (
		"Напишите, пожалуйста, *как к Вам обращаться* "
		"(в строке соообщения) и нажмите кнопку \"Отправить\"."
	),
	'phone': (
		"Введите, пожалуйста, Ваш *контакный номер телефона* "
		"(в строке соообщения) и нажмите кнопку \"Отправить\"."
	),
	'confirm': "{name}\n{phone}\n\nПодтвердить?",
	'success': (
		"Спасибо! Ваша заявка принята, специалист департамента "
		"клиентского обслуживания свяжется с Вами в ближайшее время."
	),
	'fail': "Ошибка регистрации заявки. Пожалуйста, свяжитесь с нами.",
	'notification': (
		"Заявка на обратный звонок от "
		"[{username}](tg://user?id={user_id}):\n"
		"{name}\n{phone}\n"
	)
}
buttons = {
	'back': InlineKeyboardMarkup([
		[InlineKeyboardButton("Назад", callback_data='back')]
	]),
	'confirm': InlineKeyboardMarkup([
		[InlineKeyboardButton("Подтвердить", callback_data='confirm')],
		[InlineKeyboardButton("Назад", callback_data='back')]
	])
}


@form_action
def ask_name(_update, _context):
	return 1, messages['name'], buttons['back']


@form_action
def ask_phone(update, context):
	context.user_data['name'] = update.effective_message.text
	return 2, messages['phone'], buttons['back']


@form_action
def ask_confirm(update, context):
	context.user_data['phone'] = update.effective_message.text
	return 3, messages['confirm'].format(**context.user_data), buttons['confirm']


@form_action
def done(update, context):
	try:
		context.bot.send_message(
			chat_id=context.bot_data['admin'],
			text=messages['notification'].format(
				username=update.effective_user.username or update.effective_user.id,
				user_id=update.effective_user.id,
				name=context.user_data['name'],
				phone=context.user_data['phone'],
			),
			parse_mode=ParseMode.MARKDOWN
		)
	except TelegramError as err:
		logging.error("Ошибка пересылки заявки - %s", err)
		update.callback_query.answer(messages['fail'], show_alert=True)
	else:
		update.callback_query.answer(messages['success'], show_alert=True)
	return_menu = context.bot_data['menu']['main']
	return -1, return_menu['message'], return_menu['buttons']


contact_form = form_conversation(
	entry_points=[CallbackQueryHandler(ask_name, pattern=r'^contact$')],
	states={
		1: [MessageHandler(Filters.text, ask_phone)],
		2: [MessageHandler(Filters.text, ask_confirm)],
		3: [CallbackQueryHandler(done, pattern=r'^confirm$')],
	}
)
