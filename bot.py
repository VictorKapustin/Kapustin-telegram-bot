from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from settings import PROXY, key_bot
from ephem import Mars, Venus, Jupiter, Mercury, Neptune, Uranus, Saturn, Pluto, constellation
from ephem import next_full_moon as nfm
import datetime
import re
import time
from russian_cities import russian_cities
dt = datetime.date.today()
planets_today = {'Mars': Mars(dt),
                 'Venus': Venus(dt),
                 'Jupiter': Jupiter(dt),
                 'Mercury': Mercury(dt),
                 'Neptune': Neptune(dt),
                 'Uranus': Uranus(dt),
                 'Saturn': Saturn(dt),
                 'Pluto': Pluto(dt)}


def planet(bot, update):
    planet = update.message.text.split()[1] # Берем название планеты из строки "/planet Pluto"
    if planet in planets_today:
        text = f'{planet} находится в созвездии {constellation(planets_today[planet])[1]}'
        update.message.reply_text(text)
        logging.info(f'Запрощена планета {planet}')
    else:
        text = 'Такой планеты нет в солнечной системе, попробуй ввести названия с большой буквы, например: "Venus".'
        update.message.reply_text(text)
        logging.info('Запрощена не существующая планета')

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[logging.FileHandler('bot.log', 'a', 'utf-8')]
                    )


def greet_user(bot, update):
    text = ('Введите команду "/planet" и одну из планет солнечной системы, кроме земли,'
            ' чтобы узнать в каком созвездии она находится в данный момент. Например "/planet Pluto".'
            '\nНазвания планет на английском языке: Mercury, Venus, Mars, Jupiter, Saturn, Uranus,'
            ' Neptune.')
    logging.info(text)
    update.message.reply_text(text)  # бот отвечает


def talk_to_me(bot, update):
    user_text = "Привет {}! Ты написал: {} ".format(
        update.message.chat.first_name, update.message.text)
    logging.info("Time: %s, User: %s, Chat id: %s, Message: %s,", update.message.date,
                 update.message.chat.username, update.message.chat.id, update.message.text)
    logging.info(user_text)
    update.message.reply_text(user_text)  # ответить текстом пользователя

def wordcount(bot, update):
    text = re.sub(r'[^a-zA-Zа-яА-Я ]',r'', update.message.text).split()[1:] 
    #  В полученной строке оставляем только символы a-zA-Zа-яА-Я и пробелы, дальше делим по пробелам
    if text == []:
        update.message.reply_text('Вы ввели пустое сообщение')
        return  
    update.message.reply_text('{} слова'.format(len(text)))

def next_full_moon(bot, update):
    update.message.reply_text('Следующая полная луна будет {}'.format(nfm(dt))) # TODO format time

def cities(bot, update): #TODO сделать игру без запросов каждый раз
    logging.info('Игра в города запущена')
    mybot = Updater(key_bot, request_kwargs=PROXY)
    dp = mybot.dispatcher # CommandHandler обрабатывает команды 
    update.message.reply_text('Пожалуйста введите название города с большой буквы,' 
        ' в игре участвуют города с населением более 100k. Пример: Москва')
    dp.add_handler(MessageHandler(Filters.text, city)) # Filters.text тип сообщения, talk_to_me функция    
    if update.message.text in russian_cities:
        city(bot, update)
    def city(bot, update):
        your_city = update.message.text
        russian_cities.remove(your_city)
        for city in russian_cities:
            if city[0].lower()==your_city[-1]:    
                update.message.reply_text(city)
                russian_cities.remove(city)
                letter = city[-1]
                if city[-1] in 'ъьый':
                    letter = city[-2]
                update.message.reply_text(f'Вам на "{letter.upper()}""')
                break
    
    mybot.start_polling()  # бот, начни запрашивать
    mybot.idle()  # работать бесконечно, пока не остановят
def main():
    mybot = Updater(key_bot, request_kwargs=PROXY)
    logging.info('Бот запускается')

    dp = mybot.dispatcher # CommandHandler обрабатывает команды
    dp.add_handler(CommandHandler('start', greet_user)) # при получении команды 'start' вызвать функцию greet_user 
    dp.add_handler(MessageHandler(Filters.text, talk_to_me)) # Filters.text тип сообщения, talk_to_me функция
    dp.add_handler(CommandHandler('planet', planet)) # при получении команды 'planet' вызвать функцию planet
    dp.add_handler(CommandHandler('wordcount', wordcount)) 
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
    dp.add_handler(CommandHandler('cities', cities))
    mybot.start_polling()  # бот, начни запрашивать
    mybot.idle()  # работать бесконечно, пока не остановят


main()
