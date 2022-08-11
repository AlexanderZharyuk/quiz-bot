import difflib
import os
import json
import random

import redis
import vk_api as vk

from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from quiz import get_random_question, get_questions_and_answers, get_answer
from database import update_user_last_question


def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Мой счёт', color=VkKeyboardColor.POSITIVE)
    return keyboard


def send_message(event, text):
    keyboard = create_keyboard()
    vk_api.messages.send(
        user_id=event.user_id,
        message=text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def start(event):
    greeting_message = "Привет, я бот для викторин! " \
                       "Чтобы начать - нажми кнопку Новый вопрос"
    send_message(event, text=greeting_message)


def get_new_question(event, quizzes, database):
    user_id = f"user_vk_{event.user_id}"
    question = get_random_question(quizzes)
    update_user_last_question(
        database=database,
        question=question,
        user_id=user_id
    )
    send_message(event, text=question)


def handle_solution_attempt(event, quizzes, database):
    user_answer = event.text.capitalize()
    user_id = f"user_vk_{event.user_id}"
    answer = get_answer(
        user_id=user_id,
        quizzes=quizzes,
        database=database
    )
    answers_matches = difflib.SequenceMatcher(
        None,
        user_answer,
        answer).ratio()

    if answers_matches > 0.8:
        get_users_with_questions = database.get("users").decode()
        authorized_users = json.loads(get_users_with_questions)
        authorized_users[user_id]["count"] += 1
        user_json = json.dumps(authorized_users, ensure_ascii=True)
        database.set("users", user_json)
        send_message(event, text="Правильно! Поздравляю! Для следующего "
                                 "вопроса нажми «Новый вопрос»")
    else:
        send_message(event, text="Неправильно… Попробуешь ещё раз?")


def give_up(event, quizzes, database):
    user_id = f"user_vk_{event.user_id}"
    answer = get_answer(
        user_id=user_id,
        quizzes=quizzes,
        database=database,
    )
    question = get_random_question(quizzes)
    update_user_last_question(
        database=database,
        question=question,
        user_id=user_id
    )
    send_message(event, text=f"Правильный ответ был: {answer}\n"
                             f"Чтобы получить новый вопрос нажми "
                             f"кнопку «Новый вопрос»")


def get_user_count(event, database: redis):
    user_id = f"user_vk_{event.user_id}"
    authorized_users = database.get("users").decode()
    founded_user = json.loads(authorized_users)[user_id]
    user_count = founded_user["count"]
    send_message(event, text=f"Ваш счёт: {user_count}")


if __name__ == "__main__":
    load_dotenv()
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    redis_password = os.environ["REDIS_PASSWORD"]
    vk_api_token = os.environ["VK_API_TOKEN"]

    vk_session = vk.VkApi(token=vk_api_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    quizzes = get_questions_and_answers()
    database = redis.Redis(
        host=redis_host,
        port=redis_port,
        password=redis_password
    )
    try:
        database.get("users").decode()
    except AttributeError:
        setup_db = {}
        user_json = json.dumps(setup_db, ensure_ascii=True)
        database.set("users", user_json)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.capitalize() == "Старт":
                start(event)
            elif event.text == "Новый вопрос":
                get_new_question(event, quizzes, database)
            elif event.text == "Сдаться":
                give_up(event, quizzes, database)
            elif event.text == "Мой счёт":
                get_user_count(event, database)
            else:
                handle_solution_attempt(event, quizzes, database)
