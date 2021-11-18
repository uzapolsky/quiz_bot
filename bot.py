import os
import random

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def parse_questions():
    quiz_questions = {}
    text_sections = []
    for filename in os.listdir('quiz-questions'):
        with open(f'quiz-questions/{filename}', encoding='KOI8-R') as f:
            text_sections.extend(f.read().split('\n\n'))
        
    for index, current_section in enumerate(text_sections):
        if (current_section.startswith('Вопрос') and
                index+1 < len(text_sections) and
                text_sections[index+1].startswith('Ответ')):
            key = current_section.split(':', 1)[1].strip()
            quiz_questions[key] = text_sections[index+1].split(':', 1)[1].strip()
    
    question, answer = random.choice(list(quiz_questions.items()))


def start(bot, update):
    custom_keyboard = [['Новый выпуск', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Custom Keyboard Test",
                     reply_markup=reply_markup)


def main():
    load_dotenv()
    updater = Updater(os.environ['TG_BOT_TOKEN'])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
