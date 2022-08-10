import redis


def get_answer(user_id: int, quizzes: list, database: redis):
    question = database.get(user_id).decode()
    for quiz in quizzes:
        if quiz["Вопрос"] == question:
            answer = quiz["Ответ"].split("(")[0].split(".")[0]
            return answer
