import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import json
import random

token = ''
bot = telebot.TeleBot(token=token)
def read_data():
    with open('locations.json', 'r', encoding='utf-8-sig') as f:
        try:
            locations = json.load(f)
            return locations
        except:
            print('Ошибка при чтении файла json')

def send_message(id, text):
    bot.send_message(id, text)

invalid_result_message = 'Некорректный результат, вы можете начать игру заново с помощью команды /start'
test_results = {}

def send_variant(id, test_results):
    locations = read_data()
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for vars in locations[test_results[id]['progress']]['options'].keys():
        markup.add(KeyboardButton(text=vars))
    bot.send_message(id, 'Выберите вариант действий:', reply_markup=markup)
@bot.message_handler(commands=["start"])
def start(message):
    locations = read_data()
    id = message.chat.id
    test_results[id] = {'progress': 'begin'}
    bot.send_photo(chat_id=id, photo=locations['begin']['picture']['begin'])
    bot.send_message(id, locations[test_results[id]['progress']]['description'])
    send_variant(id, test_results)

@bot.message_handler(content_types=["text"])
def process_answer(message):
    id = message.chat.id
    locations = read_data()
    try:
        if message.text in locations[test_results[id]['progress']]['options'].keys():
            if test_results[id]['progress'] != 'cyclopus':
                test_results[id]['progress'] = locations[test_results[id]['progress']]['options'][message.text]
                bot.send_photo(chat_id=id, photo=locations[test_results[id]['progress']]['picture'][test_results[id]['progress']])
                send_message(id, locations[test_results[id]['progress']]['description'])
                send_variant(id, test_results)
            elif test_results[id]['progress'] == 'cyclopus':
                game_1(message)
        else:
            send_message(id, "Неверный ответ, попробуйте еще раз. рекомендую пользоваться кнопками. Чтобы начать тест заново, введите /start")
    except:
        send_message(id, "Чтобы начать тест заново, введите /start")
def game_1(message):
    id = message.chat.id
    locations = read_data()
    number = random.randint(1, 6)
    match (message.text, number % 2):
        case ("Чётное", 0) | ("Нечётное", 1):
            test_results[id]['progress'] = 'victory'
            send_message(id, f'Выпало число:{number}.Вы победили!')
        case _:
            test_results[id]['progress'] = 'defeat'
            send_message(id, f'Выпало число:{number}.Вы проиграли!')
    bot.send_photo(chat_id=id, photo=locations[test_results[id]['progress']]['picture'][test_results[id]['progress']])
    send_message(id, locations[test_results[id]['progress']]['description'])
    with open('test_results.json', 'w') as f:
        json.dump(test_results, f)
    return test_results[id]['progress']
bot.polling()
