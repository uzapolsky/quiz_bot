import os
import random
from functools import partial

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


def parse_questions(questions_folder):
    quiz_questions = {}
    text_sections = []
    for filename in os.listdir(questions_folder):
        with open(f'{questions_folder}/{filename}', encoding='KOI8-R') as f:
            text_sections.extend(f.read().split('\n\n'))
        
    for index, current_section in enumerate(text_sections):
        if (current_section.startswith('Вопрос') and
                index+1 < len(text_sections) and
                text_sections[index+1].startswith('Ответ')):
            key = current_section.split(':', 1)[1].strip()
            quiz_questions[key] = text_sections[index+1].split(':', 1)[1].strip()
    
    return quiz_questions


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     reply_markup=reply_markup)


def new_question(bot, update, quiz_questions):
    question, answer = random.choice(list(quiz_questions.items()))
    print(question, answer)
    bot.send_message(chat_id=update.message.chat_id,
                     text=question)


def main():
    load_dotenv()
    quiz_questions = parse_questions(os.environ['QUESTIONS_FOLDER'])
    
    updater = Updater(os.environ['TG_BOT_TOKEN'])
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^Новый вопрос$'),
                   partial(new_question, quiz_questions=quiz_questions))),

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
