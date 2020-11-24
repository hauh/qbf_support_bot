"""Form to request a call back."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from telegram.ext import CallbackQueryHandler, Filters, MessageHandler
from telegram.ext.conversationhandler import ConversationHandler

from bot.menu import back, reply

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


def ask_name(update, context):
	reply(update, context, messages['name'], buttons['back'])
	return 1


def ask_phone(update, context):
	context.user_data['name'] = update.effective_message.text
	reply(update, context, messages['phone'], buttons['back'])
	return 2


def ask_confirm(update, context):
	context.user_data['phone'] = update.effective_message.text
	confirm_message = messages['confirm'].format(**context.user_data)
	reply(update, context, confirm_message, buttons['confirm'])
	return 3


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
			disable_notification=False
		)
	except TelegramError as err:
		logging.error("Ошибка пересылки заявки - %s", err)
		update.callback_query.answer(messages['fail'], show_alert=True)
	else:
		update.callback_query.answer(messages['success'], show_alert=True)
	return back(update, context)


contact_form = ConversationHandler(
	entry_points=[CallbackQueryHandler(ask_name, pattern=r'^contact$')],
	states={
		1: [MessageHandler(Filters.text, ask_phone)],
		2: [MessageHandler(Filters.text, ask_confirm)],
		3: [CallbackQueryHandler(done, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(back, pattern=r'^back$')],
	allow_reentry=True
)
