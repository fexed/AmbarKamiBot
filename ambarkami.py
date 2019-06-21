import datetime
import time
import telegram
import os
import sys
import subprocess
import atexit
import logging
import json
import datetime
import requests
import configparser
from functools import wraps
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from threading import Thread
from random import randint

LIST_OF_ADMINS = [33848223]
#fexed 33848223

def send_action(action):
	def decorator(func):
		@wraps(func)
		def command_func(update, context, *args, **kwargs):
			update.send_chat_action(chat_id=context.message.chat_id, action=action)
			return func(update, context,  *args, **kwargs)
		return command_func
	return decorator

def restricted(func):
	@wraps(func)
	def wrapped(update, context, *args, **kwargs):
		nick = context.effective_user.username
		user_id = context.effective_user.id
		if user_id not in LIST_OF_ADMINS:
			context.message.reply_text("Non autorizzato")
			user_id = nick + " [" + str(context.effective_user.id) + "]"
			logging.info("Accesso non autorizzato impedito a {}.".format(user_id))
			return
		return func(update, context, *args, **kwargs)
	return wrapped

@send_action(ChatAction.TYPING)
def pgs(bot, update):
	message = ('*PG* attualmente in game\n\n\n' +
		'*Dexio* LV4 6100xp\nUmano ammazzadraghi\n\n' +
		'*Durga Morganist III* LV4 5000xp\nMezzorca guerriera\n\n' +
		'*Kaato* LV4 5765xp\nUmano ninja\n\n' +
		'*Miryks Raanmirtah* LV4 6065xp\nElfa ranger\nCompagno animale: il lupo *Loki*\n\n' +
		'*Ragnar* LV4 6195xp\nUmano/draconide stregone\n\n' +
		'*Silva* LV4 6085xp\nTiefling druido/monaco\n_Attualmente disperso all\'interno del Dojo di Tao Xiuying_\n\n' +
		'*Zanark* LV5 6505xp\nDraconide/umano paladino\n\n')
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/pgs da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))

@send_action(ChatAction.TYPING)
def npcs(bot, update):
	message = ('*NPCS* attualmente rilevanti\n\n\n' +
		"*Alark Tonan*\nMezzelfo di 26 anni, dal fisico resistente e i capelli neri avvolti in una coda.\nAttualmente è il vostro timoniere e compagno di viaggio.\n\n" +
		"*Rofus Zanka*\nUmano rude e poco cordiale, ma molto pragmatico.\nCapitano delle guardie e governatore di Hafna\n\n" +
		"*Momok*\nAnziano umano e antico eroe guerriero, ha sconfitto uno stregone ma ne ha pagato il prezzo veneno portato 100 anni nel futuro arrivando 60 anni prima delle vostre avventure.\nVi ha contattato raccontandovi la sua storia e i suoi riti per trovarvi, e chiedendovi di fermare una volta per tutte lo Stregone delle Sette Punte\n\n" +
		"*Lich delle Sette Punte*\n?\n\n")
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/npcs da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))

def build_menu(buttons, cols, header_buttons=None, footer_buttons=None):
	menu = [buttons[i:i + cols] for i in range(0, len(buttons), cols)]
	if header_buttons:
		menu.insert(0, [header_buttons])
	if footer_buttons:
		menu.append([footer_buttons])
	return menu

@send_action(ChatAction.TYPING)
def maps(bot, update):
	button_list = [
		InlineKeyboardButton("Yeonan", callback_data="Yeonan.jpg"),
		InlineKeyboardButton("Hafna", callback_data="Hafna.jpg"),
		InlineKeyboardButton("Grillir", callback_data="Grillir.jpg"),
		InlineKeyboardButton("Melar", callback_data="Melar.jpg")
	]
	reply_markup = InlineKeyboardMarkup(build_menu(button_list, cols=2))
	message = '*Mappe* disponibili attualmente'
	update.message.reply_text(message, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
	#update.message.reply_photo(photo=open('/home/pi/ambarkami/imgs/maps/Yeonan.jpg', 'rb'), timeout=60)
	logging.info("/maps da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))

def inline_callback(bot, update):
	map = update.callback_query.data
	bot.answer_callback_query(update.callback_query.id, "Ok, sto caricando " + map + "\nAttendi pls")
	bot.delete_message(update.callback_query.message.chat.id, update.callback_query.message.message_id)
	bot.send_message(update.callback_query.message.chat.id, "In arrivo la mappa *" + map + "*\nCaricamento in corso...", parse_mode=telegram.ParseMode.MARKDOWN)
	bot.send_document(update.callback_query.message.chat.id, document=open('/home/pi/ambarkami/imgs/maps/'+map, 'rb'), timeout=60)

@restricted
@send_action(ChatAction.UPLOAD_DOCUMENT)
def logs(bot, update):
	update.message.reply_document(document=open('/home/pi/ambarkami/ambarkami.log', 'rb'))
	logging.info("/logs da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))

def stop_and_restart():
	updater.stop()
	os.execl(sys.executable, sys.executable, *sys.argv)

@restricted
@send_action(ChatAction.TYPING)
def restartbot(bot, update):
	message = '{}, riavvio'.format(update.message.from_user.username)
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/restartbot da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))
	Thread(target=stop_and_restart).start()

def d20(bot, update):
	val = str(randint(1, 20))
	message = "Lancio un D20\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d20 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def d12(bot, update):
	val = str(randint(1, 12))
	message = "Lancio un D12\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d12 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def d10(bot, update):
	val = str(randint(1, 10))
	message = "Lancio un D10\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d10 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def d8(bot, update):
	val = str(randint(1, 8))
	message = "Lancio un D8\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d8 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def d6(bot, update):
	val = str(randint(1, 6))
	message = "Lancio un D6\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d6 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def d4(bot, update):
	val = str(randint(1, 4))
	message = "Lancio un D4\n*" + val + "*"
	update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN)
	logging.info("/d4 da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id) + " [" + val + "]")

def story(bot, update):
	update.message.reply_document(document=open('/home/pi/ambarkami/txts/story', 'rb'), filename="story.txt")
	logging.info("/story da " + format(update.message.from_user.username) + " " + format(update.message.from_user.id))

configParser = configparser.RawConfigParser()
configFilePath = r'/home/pi/ambarkami/ambarkami.conf'
configParser.read_file(open(configFilePath))
apikey = configParser.get('config', 'botapikey')
bot = telegram.Bot(token=apikey)
updater = Updater(apikey)
updater.dispatcher.add_handler(CommandHandler('npcs', npcs))
updater.dispatcher.add_handler(CommandHandler('pgs', pgs))
updater.dispatcher.add_handler(CommandHandler('maps', maps))
updater.dispatcher.add_handler(CommandHandler('logs', logs))
updater.dispatcher.add_handler(CommandHandler('restartbot', restartbot))
updater.dispatcher.add_handler(CommandHandler('story', story))
#updater.dispatcher.add_handler(CommandHandler('d20', d20))
#updater.dispatcher.add_handler(CommandHandler('d12', d12))
#updater.dispatcher.add_handler(CommandHandler('d10', d10))
#updater.dispatcher.add_handler(CommandHandler('d8', d8))
#updater.dispatcher.add_handler(CommandHandler('d6', d6))
#updater.dispatcher.add_handler(CommandHandler('d4', d4))
updater.dispatcher.add_handler(CallbackQueryHandler(inline_callback))

updater.start_polling()
#onsincetime = time.asctime(time.localtime(time.time()))
onsincetime = datetime.datetime.now().strftime('%d-%m-%Y %H.%M.%S')
logging.basicConfig(filename='/home/pi/ambarkami/ambarkami.log', filemode='a+', format='%(asctime)s [%(levelname)s]: %(message)s', datefmt="%d-%m-%Y %H.%M.%S", level=logging.INFO)
logging.info("AmbarKami online")
for id in LIST_OF_ADMINS:
	bot.send_message(chat_id=id, text='*AmbarKami online*', parse_mode=telegram.ParseMode.MARKDOWN)
updater.idle()
