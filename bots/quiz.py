import json
import random
import re

import redis


QUIZ_FILEPATH = "quiz-questions/quizzes.txt"


def get_questions_and_answers() -> dict:
    questions = []
    answers = []

    with open(QUIZ_FILEPATH, "r", encoding="KOI8-R") as file:
        quiz_file = file.read().split("\n\n")

    for row in quiz_file:
        if re.search(r"Вопрос", row):
            question_text = row.split("\n")[1:]
            question = " ".join(question_text)

            if not question.find("Вопрос"):
                start_index = question.find(":") + 2
                question = question[start_index:]
            questions.append(question)

        if re.search(r"Ответ", row):
            answer_text = row.split("\n")[1:]
            answer = " ".join(answer_text)
            answers.append(answer)

    quizzes = dict(zip(questions, answers))
    questions_and_answers = {}

    for question_number, (question, answer) in enumerate(quizzes.items()):
        quiz = {
            "Вопрос": question,
            "Ответ": answer
        }
        questions_and_answers[f"question_{question_number}"] = quiz

    return questions_and_answers


def get_random_question(loaded_quiz: dict) -> str:
    questions_count = len(loaded_quiz) - 1
    random_question_number = random.randint(0, questions_count)
    quiz = f"question_{random_question_number}"
    return loaded_quiz[quiz]["Вопрос"]


def get_answer(user_id: str, quizzes: dict, database: redis):
    get_users_with_questions = database.get("users").decode()
    founded_user = json.loads(get_users_with_questions)[user_id]
    user_question = founded_user["last_asked_question"]

    for quiz in quizzes.values():
        if quiz["Вопрос"] == user_question:
            answer = quiz["Ответ"].split("(")[0].split(".")[0]
            return answer
