import difflib
import os
import json
import logging
import functools

import redis

from enum import Enum

from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, ConversationHandler)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

from quiz import get_random_question, get_questions_and_answers, get_answer
from database import update_user_last_question


class ConversationPoints(Enum):
    NEW_QUESTION = 0
    USER_ANSWER = 1


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    reply_keyboard = [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
    greeting_message = "Привет! Я бот для викторин!"

    update.message.reply_text(
        text=greeting_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True
        )
    )
    return ConversationPoints.NEW_QUESTION.value


def handle_new_question_request(
        update: Update,
        context: CallbackContext,
        quizzes: dict,
        database: redis):
    user_id = f"user_tg_{update.message.from_user.id}"
    question = get_random_question(quizzes)
    update_user_last_question(
        database=database,
        question=question,
        user_id=user_id
    )
    update.message.reply_text(question)
    return ConversationPoints.USER_ANSWER.value


def handle_solution_attempt(
        update: Update,
        context: CallbackContext,
        quizzes: dict,
        database: redis):
    user_answer = update.message.text.capitalize()
    user_id = f"user_tg_{update.message.from_user.id}"
    answer = get_answer(
        user_id=user_id,
        quizzes=quizzes,
        database=database,
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
        update.message.reply_text(
            text="Правильно! Поздравляю!"
            " Для следующего вопроса нажми «Новый вопрос»",
        )
        return ConversationPoints.NEW_QUESTION.value

    update.message.reply_text("Неправильно… Попробуешь ещё раз?")
    return ConversationPoints.USER_ANSWER.value


def give_up(
        update: Update,
        context: CallbackContext,
        database: redis,
        quizzes: dict):
    user_id = f"user_tg_{update.message.from_user.id}"
    answer = get_answer(
        user_id=user_id,
        quizzes=quizzes,
        database=database,
    )
    question = get_random_question(quizzes)
    update_user_last_question(
        question=question,
        database=database,
        user_id=user_id
    )

    update.message.reply_text(f"Правильный ответ был: {answer}\n"
                              f"Чтобы продолжить нажми кнопку «Новый вопрос»")
    return ConversationPoints.NEW_QUESTION.value


def get_user_count(update: Update, context: CallbackContext, database: redis):
    user_id = f"user_tg_{update.message.from_user.id}"
    authorized_users = database.get("users").decode()
    founded_user = json.loads(authorized_users)[user_id]
    user_count = founded_user["count"]
    update.message.reply_text(f"Ваш счёт: {user_count}")

    return ConversationPoints.NEW_QUESTION.value


def get_error(update, error):
    logger.warning("Update '%s' caused error '%s'", update, error)


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    load_dotenv()
    redis_host = os.environ["REDIS_HOST"]
    redis_port = os.environ["REDIS_PORT"]
    redis_password = os.environ["REDIS_PASSWORD"]
    telegram_bot_token = os.environ["TELEGRAM_TOKEN"]

    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                        level=logging.INFO)

    updater = Updater(token=telegram_bot_token, use_context=True)
    dp = updater.dispatcher

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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            ConversationPoints.NEW_QUESTION.value:
                {
                    MessageHandler(
                        Filters.regex("^(Новый вопрос)$"),
                        functools.partial(
                            handle_new_question_request,
                            quizzes=quizzes,
                            database=database
                        )
                    ),
                    MessageHandler(
                        Filters.regex("^(Мой счёт)$"),
                        functools.partial(
                            get_user_count,
                            database=database
                        )
                    )
                },

            ConversationPoints.USER_ANSWER.value:
                [
                    CommandHandler(
                        "cancel",
                        cancel
                    ),
                    MessageHandler(
                        Filters.regex("^(Сдаться)$"),
                        functools.partial(
                            give_up,
                            quizzes=quizzes,
                            database=database
                        )
                    ),
                    MessageHandler(
                        Filters.regex("^(Мой счёт)$"),
                        functools.partial(
                            get_user_count,
                            database=database
                        )
                    ),
                    MessageHandler(
                        Filters.text,
                        functools.partial(
                            handle_solution_attempt,
                            quizzes=quizzes,
                            database=database
                        )
                    )
                ],
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
