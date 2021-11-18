import os
import random

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from dotenv import load_dotenv

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


def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def main():
    load_dotenv()
    updater = Updater(os.environ['TG_BOT_TOKEN'])

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
