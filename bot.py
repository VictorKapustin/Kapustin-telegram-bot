from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from settings import PROXY, key_bot

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

def greet_user(bot, update):
    text = 'Вызван /start'
    logging.info(text)
    update.message.reply_text(text) #бот отвечает 

def talk_to_me(bot, update):
    user_text = "Привет {}! Ты написал: {} ".format(update.message.chat.first_name, update.message.text)
    logging.info("Time: %s, User: %s, Chat id: %s, Message: %s,", update.message.date, 
                update.message.chat.username, update.message.chat.id, update.message.text)
    logging.info(user_text)
    update.message.reply_text(user_text) # ответить текстом пользователя


def main():
    mybot= Updater(key_bot, request_kwargs=PROXY)

    logging.info('Бот запускается')

    dp=mybot.dispatcher
    dp.add_handler(CommandHandler('start', greet_user)) #CommandHandler обрабатывает команды
    # при получении команды 'start' вызвать функцию greet_user
    dp.add_handler(MessageHandler(Filters.text, talk_to_me)) # Обрабатывает сообщения, 
    # Filters.text тип сообщения, talk_to_me функция 
    mybot.start_polling() # бот, начни запрашивать 
    mybot.idle() # работать бесконечно, пока не остановят


main()