"""Contact customer form."""


from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
	Filters, ConversationHandler, MessageHandler, CallbackQueryHandler)


form = {
	'name': "Как к вам обращаться?",
	'phone': "Введите контакный номер телефона.",
	'time': "Укажите удобное время для звонка.",
	'confirm': "{name}\n{phone}\n{time}\n\nПодвердить?",
	'success': "Заявка зарегистрирована."
}
notification = (
	"Заявка на обратный звонок от "
	"[{username}](tg://user?id={user_id}):\n"
	"{name}\n{phone}\n{time}"
)

back_btn = [InlineKeyboardButton("Назад", callback_data='back')]
confirm_btn = [InlineKeyboardButton("Подвердить", callback_data='confirm')]
back = InlineKeyboardMarkup([back_btn])
confirm = InlineKeyboardMarkup([confirm_btn, back_btn])


def form_action(callback):
	def next_action(update, context):
		if last_message := context.user_data.get('last_message'):
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
def ask_time(update, context):
	context.user_data['phone'] = update.effective_message.text
	return 3, form['time'], back


@form_action
def ask_confirm(update, context):
	context.user_data['time'] = update.effective_message.text
	return 4, form['confirm'].format(**context.user_data), confirm


def done(update, context):
	update.callback_query.answer(form['success'], show_alert=True)
	text = notification.format(
		username=update.effective_user.username or update.effective_user.id,
		user_id=update.effective_user.id,
		**context.user_data
	)
	update.effective_chat.send_message(text, parse_mode='Markdown')
	return end(update, context)


@form_action
def end(_update, context):
	return_menu = context.bot_data['menu']['main']
	return -1, return_menu['message'], return_menu['buttons']


contact_form = ConversationHandler(
	entry_points=[CallbackQueryHandler(ask_name, pattern=r'^contact$')],
	states={
		1: [MessageHandler(Filters.text, ask_phone)],
		2: [MessageHandler(Filters.text, ask_time)],
		3: [MessageHandler(Filters.text, ask_confirm)],
		4: [CallbackQueryHandler(done, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(end, pattern=r'^back$')],
	allow_reentry=True,
)
