"""Base conversation form."""

from functools import partial

from telegram.ext import CallbackQueryHandler, ConversationHandler


def form_action(callback):
	def next_action(update, context):
		if update.callback_query:
			update.callback_query.answer()
		if last_message := context.user_data.pop('last_message', None):
			last_message.delete()
		next_step, text, btn = callback(update, context)
		msg = update.effective_message.reply_markdown(text=text, reply_markup=btn)
		context.user_data['last_message'] = msg
		return next_step
	return next_action


@form_action
def end(_update, context):
	return_menu = context.bot_data['menu']['main']
	return -1, return_menu['message'], return_menu['buttons']


form_conversation = partial(
	ConversationHandler,
	fallbacks=[CallbackQueryHandler(end, pattern=r'^back$')],
	allow_reentry=True
)
