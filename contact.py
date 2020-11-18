"""Contact customer form."""

import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import TelegramError
from telegram.ext import (
	Filters, ConversationHandler, MessageHandler, CallbackQueryHandler)


form = {
	'name': (
		"Напишите, пожалуйста, как к Вам обращаться "
		"(в строке соообщения) и нажмите кнопку \"Отправить\"."
	),
	'phone': (
		"Введите, пожалуйста, Ваш контакный номер телефона "
		"(в строке соообщения) и нажмите кнопку \"Отправить\"."
	),
	'confirm': "{name}\n{phone}\n\nПодтвердить?",
	'success': (
		"Спасибо! Ваша заявка принята, специалист департамента "
		"клиентского обслуживания свяжется с Вами в ближайшее время."
	),
	'fail': "Ошибка регистрации заявки. Пожалуйста, свяжитесь с нами."
}
notification = (
	"Заявка на обратный звонок от "
	"[{username}](tg://user?id={user_id}):\n"
	"{name}\n{phone}\n"
)

back_btn = [InlineKeyboardButton("Назад", callback_data='back')]
confirm_btn = [InlineKeyboardButton("Подтвердить", callback_data='confirm')]
back = InlineKeyboardMarkup([back_btn])
confirm = InlineKeyboardMarkup([confirm_btn, back_btn])


def form_action(callback):
	def next_action(update, context):
		if update.callback_query:
			update.callback_query.answer()
		if last_message := context.user_data.pop('last_message', None):
			last_message.delete()
		next_step, text, buttons = callback(update, context)
		msg = update.effective_chat.send_message(text=text, reply_markup=buttons)
		context.user_data['last_message'] = msg
		return next_step
	return next_action


@form_action
def ask_name(_update, _context):
	return 1, form['name'], back


@form_action
def ask_phone(update, context):
	context.user_data['name'] = update.effective_message.text
	return 2, form['phone'], back


@form_action
def ask_confirm(update, context):
	context.user_data['phone'] = update.effective_message.text
	return 3, form['confirm'].format(**context.user_data), confirm


def done(update, context):
	try:
		context.bot.send_message(
			chat_id=context.bot_data['admin'],
			text=notification.format(
				username=update.effective_user.username or update.effective_user.id,
				user_id=update.effective_user.id,
				name=context.user_data['name'],
				phone=context.user_data['phone'],
			),
			parse_mode='Markdown'
		)
	except TelegramError as err:
		logging.error("Ошибка пересылки заявки - %s", err)
		update.callback_query.answer(form['fail'], show_alert=True)
	else:
		update.callback_query.answer(form['success'], show_alert=True)
	return end(update, context)


@form_action
def end(_update, context):
	return_menu = context.bot_data['menu']['main']
	return -1, return_menu['message'], return_menu['buttons']


contact_form = ConversationHandler(
	entry_points=[CallbackQueryHandler(ask_name, pattern=r'^contact$')],
	states={
		1: [MessageHandler(Filters.text, ask_phone)],
		2: [MessageHandler(Filters.text, ask_confirm)],
		3: [CallbackQueryHandler(done, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(end, pattern=r'^back$')],
	allow_reentry=True,
)
