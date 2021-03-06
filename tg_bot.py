import os
import random
from functools import partial
from parse_questions import parse_questions

import redis
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

QUESTION, ANSWER = range(2)
KEYBOARD = [['Новый вопрос', 'Сдаться'],
                       ['Мой счёт']]
REPLY_MARKUP = ReplyKeyboardMarkup(KEYBOARD, one_time_keyboard=True)


def start(update, context):
    
    update.message.reply_text('Привет! Начинаем викторину!', reply_markup=REPLY_MARKUP)
    return QUESTION


def handle_new_question_request(update, context, quiz_questions, db):
    
    question, _ = random.choice(list(quiz_questions.items()))
    tg_user_id = 'tg_{}'.format(update.message.from_user['id'])
    db.set(tg_user_id, quiz_questions[question])
    update.message.reply_text(text=question)
    return ANSWER


def handle_solution_attempt(update, context, db):
    
    tg_user_id = 'tg_{}'.format(update.message.from_user['id'])
    user_answer = update.message.text
    answer = db.get(tg_user_id)
    correct_answer_raw = answer.split('.', 1)[0]
    correct_answer = correct_answer_raw.split('(', 1)[0]

    if user_answer.lower() ==  correct_answer.lower():
        update.message.reply_text(
            'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос".',
            reply_markup=REPLY_MARKUP,
        )
        return QUESTION

    update.message.reply_text(
        'Неправильно… Попробуешь ещё раз?',
        reply_markup=REPLY_MARKUP,
    )
    return ANSWER


def handle_give_up(update, context, quiz_questions, db):

    tg_user_id = 'tg_{}'.format(update.message.from_user['id'])
    answer = db.get(tg_user_id)
    
    update.message.reply_text(
        'Правильный ответ:\n{0}'.format(answer),
        reply_markup=REPLY_MARKUP,
    )

    handle_new_question_request(update, context, quiz_questions, db)


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
        password=os.environ['REDIS_PASSWORD'],
        decode_responses=True
    )
    dp = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [
                MessageHandler(Filters.regex('^Новый вопрос$'),
                               partial(handle_new_question_request,
                                       quiz_questions=quiz_questions,
                                       db=db)),
            ],
            ANSWER: [
                MessageHandler(Filters.regex('^Сдаться$'),
                               partial(handle_give_up,
                                       quiz_questions=quiz_questions,
                                       db=db)),
                MessageHandler(Filters.text, partial(handle_solution_attempt,
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
