import os
import random
from functools import partial

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

QUESTION, ANSWER = range(2)
KEYBOARD = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
REPLY_MARKUP = ReplyKeyboardMarkup(KEYBOARD, one_time_keyboard=True)


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


def start(update, context):
    
    update.message.reply_text('Привет! Начинаем викторину!', reply_markup=REPLY_MARKUP)
    return QUESTION


def handle_new_question_request(update, context, quiz_questions, db):
    question, answer = random.choice(list(quiz_questions.items()))
    tg_user_id = 'tg_{}'.format(update.message.from_user['id'])
    db.set(tg_user_id, question)
    update.message.reply_text(text=question)
    return ANSWER


def handle_solution_attempt(update, context, quiz_questions, db):
    tg_user_id = 'tg_{}'.format(update.message.from_user['id'])
    answer = update.message.text
    question = db.get(tg_user_id).decode('UTF-8')
    correct_answer_full = quiz_questions[question].split('.', 1)[0]
    correct_answer_short = correct_answer_full.split('(', 1)[0]

    if answer.lower() ==  correct_answer_short.lower():
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".',
            reply_markup=REPLY_MARKUP,
        )
        return QUESTION
    else:
        update.message.reply_text(
            'Неправильно… Попробуешь ещё раз?',
            reply_markup=REPLY_MARKUP,
        )
        return ANSWER


def done(update, context):

    user_data = context.user_data

    update.message.reply_text(
        'Возвращайтесь еще!',
        reply_markup=ReplyKeyboardRemove(),
    )

    user_data.clear()
    return ConversationHandler.END


def main():
    load_dotenv()
    quiz_questions = parse_questions(os.environ['QUESTIONS_FOLDER'])
    
    updater = Updater(os.environ['TG_BOT_TOKEN'])
    db = redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=os.environ['REDIS_PORT'],
        password=os.environ['REDIS_PASSWORD']
    )
    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [
                MessageHandler(Filters.regex('^Новый вопрос$'), partial(handle_new_question_request,
                                                                        quiz_questions=quiz_questions,
                                                                        db=db)),
            ],
            ANSWER: [
                MessageHandler(Filters.text, partial(handle_solution_attempt,
                                                     quiz_questions=quiz_questions,
                                                     db=db)),
            ],
        
        },
        fallbacks=[MessageHandler(Filters.regex('^Конец$'), done)], 
    )
    dp.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
