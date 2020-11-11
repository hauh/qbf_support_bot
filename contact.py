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


def ask_name(update, _context):
	update.effective_chat.send_message(text=form['name'], reply_markup=back)
	return 1


def ask_phone(update, context):
	context.user_data['name'] = update.effective_message.text
	update.effective_chat.send_message(text=form['phone'], reply_markup=back)
	return 2


def ask_time(update, context):
	context.user_data['phone'] = update.effective_message.text
	update.effective_chat.send_message(text=form['time'], reply_markup=back)
	return 3


def ask_confirm(update, context):
	context.user_data['time'] = update.effective_message.text
	text = form['confirm'].format(**context.user_data)
	update.effective_chat.send_message(text=text, reply_markup=confirm)
	return 4


def done(update, context):
	update.callback_query.answer(form['success'], show_alert=True)
	text = notification.format(
		username=update.effective_user.username or update.effective_user.id,
		user_id=update.effective_user.id,
		**context.user_data
	)
	update.effective_chat.send_message(text, parse_mode='Markdown')
	return -1


contact_form = ConversationHandler(
	entry_points=[CallbackQueryHandler(ask_name, pattern=r'^contact$')],
	states={
		1: [MessageHandler(Filters.text, ask_phone)],
		2: [MessageHandler(Filters.text, ask_time)],
		3: [MessageHandler(Filters.text, ask_confirm)],
		4: [CallbackQueryHandler(done, pattern=r'^confirm$')],
	},
	fallbacks=[CallbackQueryHandler(lambda *_: -1, pattern=r'^back$')],
	allow_reentry=True,
)
