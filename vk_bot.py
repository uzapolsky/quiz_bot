import os
import random
from dotenv import load_dotenv
import redis
import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkEventType, VkLongPoll

from parse_questions import parse_questions


def new_question(event, vk, keyboard, quiz_questions,db):
    vk_user_id = 'vk_{}'.format(event.user_id)
    question, _ = random.choice(list(quiz_questions.items()))
    db.set(vk_user_id, quiz_questions[question])
    vk.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard(),
    )

def give_up(event, vk, keyboard, db):
    vk_user_id = 'vk_{}'.format(event.user_id)
    answer = db.get(vk_user_id).decode('UTF-8')
    vk.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=random.randint(1,1000),
        keyboard=keyboard.get_keyboard()
    )
    
def solution_attempt(event, vk, keyboard, db):
    vk_user_id = 'vk_{}'.format(event.user_id)
    answer = db.get(vk_user_id).decode('UTF-8')
    correct_answer_raw = answer.split('.', 1)[0]
    correct_answer = correct_answer_raw.split('(', 1)[0]
    if event.text == correct_answer:
        vk.messages.send(
            user_id=event.user_id,
            message="Правильно! Поздравляю! "
            "Для следующего вопроса нажми «Новый вопрос»",
            random_id=random.randint(1,1000),
            keyboard=keyboard.get_keyboard()
        )
    else:
        vk.messages.send(
            user_id=event.user_id,
            message="Неправильно... Попробуешь ещё раз?",
            random_id=random.randint(1,1000),
            keyboard=keyboard.get_keyboard()
        )


def main():
    load_dotenv()

    db = redis.Redis(
        host=os.environ['REDIS_HOST'],
        port=os.environ['REDIS_PORT'],
        password=os.environ['REDIS_PASSWORD']
    )
    quiz_questions = parse_questions(os.environ['QUESTIONS_FOLDER'])

    vk_session = vk_api.VkApi(token=os.environ['VK_BOT_TOKEN'])
    vk = vk_session.get_api()

    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.PRIMARY)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.PRIMARY)

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Новый вопрос':
                new_question(event, vk, keyboard, quiz_questions, db)
            elif event.text == 'Сдаться':
                give_up(event, vk, keyboard, db)
                new_question(event, vk, keyboard, quiz_questions, db)
            else:
                solution_attempt(event, vk, keyboard, db)


if __name__ == '__main__':
    main()