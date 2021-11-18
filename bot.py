import os
import random


def main():
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


if __name__ == '__main__':
    main()