import random
import re


QUIZ_FILEPATH = "quiz-questions/quizzes.txt"


def get_questions_and_answers() -> list:
    questions = []
    answers = []

    with open(QUIZ_FILEPATH, "r", encoding="KOI8-R") as file:
        quiz_file = file.read().split("\n\n")

    for row in quiz_file:
        if re.search("Вопрос", row):
            question_text = row.split("\n")[1:]
            question = " ".join(question_text)

            if not question.find("Вопрос"):
                start_index = question.find(":") + 2
                question = question[start_index:]
            questions.append(question)

        if re.search("Ответ", row):
            answer_text = row.split("\n")[1:]
            answer = " ".join(answer_text)
            answers.append(answer)

    quizzes = dict(zip(questions, answers))
    questions_and_answers = []

    for question, answer in quizzes.items():
        quiz = {
            "Вопрос": question,
            "Ответ": answer
        }
        questions_and_answers.append(quiz)

    return questions_and_answers


def get_random_question(loaded_quiz: list) -> str:
    questions_count = len(loaded_quiz) - 1
    random_question_index = random.randint(0, questions_count)
    return loaded_quiz[random_question_index]["Вопрос"]
