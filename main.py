import random
import telebot
import time
import schedule
import threading
import gtts
from telebot import types

bot = telebot.TeleBot('7622464046:AAHK0OuaeaP5nvGuAU71w-Ha9WQQGwlmhy8')
chat_id = {}
file = open("Тексты/slova.txt", "r", encoding="utf-8")
text = file.readlines()
user_current_question = {}


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, "Привет! Круто, что ты решил увеличить свои знания, это достойно уважения! "
                                      "Я буду присылать тебе слова каждый час. Не пропусти их!")
    chat_id[message.chat.id] = 0


def send_test2():
    for user_id in chat_id:
        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton("Пройти тест", callback_data="start_test")
        markup.add(button)
        bot.send_message(user_id, "Самое время проверить ваши знания!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "start_test")
def handle_test(call):
    user_id = call.message.chat.id
    choise_mas = []
    choise_answer = []

    for i in range(len(text)):
        if "—" in text[i]:
            choise_answer.append(i)
            if i < chat_id[user_id]:
                choise_mas.append(i)

    if not choise_mas:
        bot.send_message(user_id, "Нет доступных слов для тестирования.")
        return

    rand_word = random.choice(choise_mas)
    correct_word = ' '.join(text[rand_word].split('—')[0].strip().split())
    russian_word = text[rand_word].split('—')[1].strip()

    options = [correct_word]
    while len(options) < 4:
        rand_other = random.choice(choise_answer)
        other_word = ' '.join(text[rand_other].split('—')[0].strip().split())
        if other_word not in options:
            options.append(other_word)

    random.shuffle(options)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [types.KeyboardButton(option) for option in options]
    markup.add(*buttons)

    bot.send_message(user_id, f"Какое слово в английском означает '{russian_word}'?", reply_markup=markup)

    user_current_question[user_id] = {
        "correct": correct_word,
        "russian": russian_word,
    }


@bot.message_handler(func=lambda message: message.chat.id in user_current_question)
def check_answer(message):
    user_id = message.chat.id
    user_answer = message.text.strip()
    correct_answer = user_current_question[user_id]["correct"]

    if user_answer.lower() == correct_answer.lower():
        bot.send_message(user_id, "✅ Правильно!")
    else:
        bot.send_message(user_id, f"❌ Неправильно! Правильный ответ: {correct_answer}")

    del user_current_question[user_id]
    markup = types.ReplyKeyboardRemove()
    bot.send_message(user_id, 'Спасибо за ваш ответ!', reply_markup=markup)


def send_message():

    for user_id in chat_id:
        for i in range(3):
            bot.send_message(user_id, text[chat_id[user_id] + i].strip())
        eng_word = ' '.join(text[chat_id[user_id]].split('—')[0].strip().split())
        tts = gtts.gTTS(eng_word)
        tts.save("Озвучка/Прослушай правильное произношение.mp3")

        with open(r'Озвучка/Прослушай правильное произношение.mp3', 'rb') as audio:
            bot.send_audio(user_id, audio)

        chat_id[user_id] += 4
        print(f"Сообщение отправлено пользователю {user_id}")


schedule.every(10).seconds.do(send_message)
schedule.every(7).days.do(send_test2)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(1)


threading.Thread(target=run_schedule, daemon=True).start()
bot.polling(none_stop=True)
