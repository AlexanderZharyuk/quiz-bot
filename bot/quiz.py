import re
import os
import json


def parse_questions_and_answers() -> tuple:
    quiz_filenames = os.listdir('../quiz-questions')
    questions = []
    answers = []

    for filename in quiz_filenames:
        filepath = os.path.join('../quiz-questions', filename)

        with open(filepath, 'r', encoding='KOI8-R') as file:
            quiz_file = file.read().split('\n\n')

        for row in quiz_file:
            if re.search('Вопрос', row):
                question_text = row.split('\n')[1:]
                question = ' '.join(question_text)

                if not question.find('Вопрос'):
                    start_index = question.find(':') + 2
                    question = question[start_index:]

                questions.append(question)

            if re.search('Ответ', row):
                answer_text = row.split('\n')[1:]
                answer = ' '.join(answer_text)
                answers.append(answer)

    return questions, answers


def get_questions_and_answers() -> dict:
    questions, answers = parse_questions_and_answers()
    questions_and_answers = dict(zip(questions, answers))
    questions = {}

    for question_number, (question, answer) in enumerate(
            questions_and_answers.items(),
            start=1):
        questions[question_number] = {
            "Вопрос": question,
            "Ответ": answer
        }

    return questions


def create_quiz_file() -> None:
    questions = get_questions_and_answers()

    with open('../quiz-questions/qa.json', 'w') as json_file:
        json.dump(questions, json_file, ensure_ascii=False, indent=4)
