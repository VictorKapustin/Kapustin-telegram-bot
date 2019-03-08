import logging
import datetime
import re
import requests
from glob import glob
from random import choice

from ephem import Mars, Venus, Jupiter, Mercury, Neptune, Uranus, Saturn, Pluto
from ephem import next_full_moon as nfm, constellation
from emoji import emojize
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton

from settings import PROXY, key_bot, key_weather, USER_EMOJI, russian_cities


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[logging.FileHandler('bot.log', 'a', 'utf-8')]
                    )

dt = datetime.date.today()
planets_today = {'Mars': Mars(dt),
                 'Venus': Venus(dt),
                 'Jupiter': Jupiter(dt),
                 'Mercury': Mercury(dt),
                 'Neptune': Neptune(dt),
                 'Uranus': Uranus(dt),
                 'Saturn': Saturn(dt),
                 'Pluto': Pluto(dt)}


def planet(bot, update, user_data):

    if update.message.text == '/planet':
        text = 'Пожалуйста введите команду "/planet" и название планеты с большой буквы. Например /planet Pluto'
        update.message.reply_text(text, reply_markup=get_keyboard())
    else:
        planet = update.message.text.split()[1] # Берем название планеты из строки "/planet Pluto"
        if planet in planets_today:
            text = f'{planet} находится в созвездии {constellation(planets_today[planet])[1]}'
            update.message.reply_text(text, reply_markup=get_keyboard())
            logging.info(f'Запрощена планета {planet}')
        else:
            text = 'Такой планеты нет в солнечной системе, попробуй ввести названия с большой буквы, например: "Venus".'
            update.message.reply_text(text, reply_markup=get_keyboard())
            logging.info('Запрощена не существующая планета')


def greet_user(bot, update, user_data):
    text = ('Введите команду "/planet" и одну из планет солнечной системы, кроме земли,'
            ' чтобы узнать в каком созвездии она находится в данный момент. Например "/planet Pluto".'
            '\nНазвания планет на английском языке: Mercury, Venus, Mars, Jupiter, Saturn, Uranus,'
            ' Neptune.')
    logging.info(text)
    update.message.reply_text(text, reply_markup=get_keyboard())  # бот отвечает


def talk_to_me(bot, update, user_data):
    if user_data['is_playing']:
        cities(bot, update, user_data)
    else:
        user_text = "Привет {}! Ты написал: {} ".format(
            update.message.chat.first_name, update.message.text)
        logging.info("Time: %s, User: %s, Chat id: %s, Message: %s,", update.message.date,
                    update.message.chat.username, update.message.chat.id, update.message.text)
        logging.info(user_text)
        update.message.reply_text(user_text, reply_markup=get_keyboard())  # ответить текстом пользователя


def wordcount(bot, update, user_data):
    text = re.sub(r'[^a-zA-Zа-яА-Я ]', r'', update.message.text).split()[1:]
    #  В полученной строке оставляем только символы a-zA-Zа-яА-Я и пробелы, дальше делим по пробелам
    if text == []:
        update.message.reply_text('Вы ввели пустое сообщение, напишите какое-нибудь сообщение и' +
                                  ' я подсчитаю количество слов в нем.')
        return  
    update.message.reply_text('{} слова'.format(len(text)), reply_markup=get_keyboard())


def next_full_moon(bot, update, user_data):
    emoji = emojize(USER_EMOJI[4], use_aliases=True)
    update.message.reply_text(f'Следующая полная луна будет {nfm(dt)} {emoji}', reply_markup=get_keyboard()) # TODO format time


def cities(bot, update, user_data): 
        if update.message.text in russian_cities and (user_data['letter'] == update.message.text[0] or user_data['letter']==''):
        # Условие: город пользователя в списке городов и это либо первый город, который он называет либо на правильную букву    
            your_city = update.message.text # Город пользователя
            russian_cities.remove(your_city) # удаление города из списка городов
            your_city_letter = your_city[-1] # Последняя буква города пользователя 
            if your_city_letter in 'ъьыйц':   # Если последняя буква города пользователя в 'ъьый'
                your_city_letter = your_city[-2] # То буквой становится предпоследняя
            
            is_there_a_city = 0
            for city in russian_cities:     # Перебор списка городов
                if city[0].lower() == your_city_letter:  # Если первая буква города равна последней букве города пользователя
                    is_there_a_city += 1
            if is_there_a_city == 0:
                update.message.reply_text('Поздравляю, вы победили', reply_markup=get_keyboard())
                cities_off(bot, update, user_data)
                return
            for city in russian_cities:     # Перебор списка городов
                if city[0].lower()==your_city_letter: # Если первая буква города равна последней букве города пользователя
                    update.message.reply_text(city) # Отправить город
                    russian_cities.remove(city)    # Удалить город из списка
                    letter = city[-1].upper() # Переменная содержит последнюю букву города, если она не в 'ъьый'
                    if city[-1] in 'ъьыйц':
                        letter = city[-2].upper()
                    update.message.reply_text(f'Вам на "{letter}"', reply_markup=get_keyboard()) # Сообщение, на какую букву надо написать город юзеру
                    user_data['letter'] = letter # Сохранение буквы для последующей проверки 
                    break

            for city in russian_cities:
                if city[0] == letter:
                    return
            update.message.reply_text('Вы проиграли, городов на такую букву нет.', reply_markup=get_keyboard())
        else:
            update.message.reply_text('Вы ввели не правильный город, если хотите закончить игру, напишите "/stop"', reply_markup=get_keyboard())


def cities_on(bot, update, user_data):
    user_data['is_playing'] = True
    user_data['letter'] = ""
    # Создание переменной, по которой сверяется, что город пользователя начинается на нужную букву
    update.message.reply_text('Пожалуйста введите название города с большой буквы,' 
                              ' в игре участвуют города с населением более 100k. Пример: Москва', reply_markup=get_keyboard())
    logging.info('Игра в города запущена') 


def cities_off(bot, update, user_data):
    user_data['is_playing'] = False
    update.message.reply_text('Вы закончили играть в города')


def weather_city(bot, update, user_data):
    if len(update.message.text.split()) == 1:
        update.message.reply_text('Пожалуйста введите команду /weather и название города латиницей.' +
                                  ' Например /weather Moscow', reply_markup=get_keyboard())
    else:
        city = update.message.text.split()[1]
        weather_url = 'http://api.worldweatheronline.com/premium/v1/weather.ashx'
        parameters = {'key': key_weather, 'q': city,
                      'format': 'json', 'num_of_days': '1'}
        result = requests.get(weather_url, params=parameters)
        weather = result.json()
        w = weather['data']['current_condition'][0]['temp_C']
        update.message.reply_text(f'Сейчас в городе {city} {w} градусов цельсия', reply_markup=get_keyboard())


def image(bot, update, user_data):
    all_pictures = glob('pom/pom*.jpg')
    take_picture = choice(all_pictures)
    bot.send_photo(chat_id=update.message.chat.id, photo=open(take_picture, 'rb'))


def get_contact(bot, update, user_data):

    update.message.reply_text(
        'Спасибо {}, твой телефон добавлен в базу данных(нет).'.format(update.message.chat.first_name))

def get_location(bot, update, user_data):
    update.message.reply_text(
        'Спасибо {}, твоё местоположение добавлено в базу данных(нет).'.format(update.message.chat.first_name))

def get_keyboard():
    contact_button = KeyboardButton('Контактные данные', request_contact=True)
    location_button = KeyboardButton('Геолокация', request_location=True)
    keyboard = ReplyKeyboardMarkup([['/planet', 'Игра в города', '/next_full_moon', contact_button],
                                    ['/image', '/wordcount', 'Погода', location_button]],
                                   resize_keyboard=True)
    return keyboard


def main():
    mybot = Updater(key_bot, request_kwargs=PROXY)
    logging.info('Бот запускается')

    dp = mybot.dispatcher # CommandHandler обрабатывает команды
    dp.add_handler(CommandHandler('start', greet_user, pass_user_data=True))
    dp.add_handler(CommandHandler('cities', cities_on, pass_user_data=True))
    dp.add_handler(CommandHandler('stop', cities_off, pass_user_data=True))
    dp.add_handler(CommandHandler('planet', planet, pass_user_data=True))
    dp.add_handler(CommandHandler('wordcount', wordcount, pass_user_data=True))
    dp.add_handler(CommandHandler('next_full_moon', next_full_moon, pass_user_data=True))
    dp.add_handler(CommandHandler('weather', weather_city, pass_user_data=True))
    dp.add_handler(CommandHandler('image', image, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Погода)$', weather_city, pass_user_data=True))
    dp.add_handler(RegexHandler('^(Игра в города)$', cities_on, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.contact, get_contact, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.location, get_location, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, talk_to_me, pass_user_data=True))
    mybot.start_polling()  # бот, начни запрашивать
    mybot.idle()  # работать бесконечно, пока не остановят


main()
