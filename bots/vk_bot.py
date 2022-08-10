import difflib
import os
import random

import redis
import vk_api as vk

from dotenv import load_dotenv
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

from general_functions import get_answer
from quiz import get_random_question, get_questions_and_answers


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
    question = get_random_question(quizzes)
    database.set(event.user_id, question)
    send_message(event, text=question)


def handle_solution_attempt(event, quizzes, database):
    user_answer = event.text.capitalize()
    answer = get_answer(
        user_id=event.user_id,
        quizzes=quizzes,
        database=database)
    answers_matches = difflib.SequenceMatcher(
        None,
        user_answer,
        answer).ratio()

    if answers_matches > 0.8:
        send_message(event, text="Правильно! Поздравляю! Для следующего "
                                 "вопроса нажми «Новый вопрос»")
    else:
        send_message(event, text="Неправильно… Попробуешь ещё раз?")


def give_up(event, quizzes, database):
    answer = get_answer(
        user_id=event.user_id,
        quizzes=quizzes,
        database=database)
    question = get_random_question(quizzes)
    database.set(event.user_id, question)

    send_message(event, text=f"Правильный ответ был: {answer}\n"
                             f"Чтобы получить новый вопрос нажми "
                             f"кнопку «Новый вопрос»")


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

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text.capitalize() == "Старт":
                start(event)
            elif event.text == "Новый вопрос":
                get_new_question(event, quizzes, database)
            elif event.text == "Сдаться":
                give_up(event, quizzes, database)
            else:
                handle_solution_attempt(event, quizzes, database)
