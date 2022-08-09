import difflib
import os
import logging

from enum import Enum

import redis

from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext, ConversationHandler)
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from dotenv import load_dotenv

from quiz import get_random_question, get_questions_and_answers


class ConversationPoints(Enum):
    NEW_QUESTION = 0
    USER_ANSWER = 1


logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
redis_host = os.environ["REDIS_HOST"]
redis_port = os.environ["REDIS_PORT"]
redis_password = os.environ["REDIS_PASSWORD"]
database = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password
)


def get_answer(update: Update):
    question = database.get(update.message.from_user.id).decode()
    questions_and_answers = get_questions_and_answers()
    for quiz in questions_and_answers:
        if quiz["Вопрос"] == question:
            answer = quiz["Ответ"].split("(")[0].split(".")[0]
            return answer


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


def handle_new_question_request(update: Update, context: CallbackContext):
    question = get_random_question()
    database.set(update.message.from_user.id, question)
    update.message.reply_text(question)
    return ConversationPoints.USER_ANSWER.value


def handle_solution_attempt(update: Update, context: CallbackContext):
    user_answer = update.message.text.capitalize()
    answer = get_answer(update)
    answers_matches = difflib.SequenceMatcher(None, user_answer, answer).ratio()

    if answers_matches > 0.8:
        update.message.reply_text(
            text="Правильно! Поздравляю!"
            " Для следующего вопроса нажми «Новый вопрос»",
        )
        return ConversationPoints.NEW_QUESTION.value

    update.message.reply_text("Неправильно… Попробуешь ещё раз?")
    return ConversationPoints.USER_ANSWER.value


def user_give_up(update: Update, context: CallbackContext):
    correct_answer = get_answer(update)
    new_question = get_random_question()
    database.set(update.message.from_user.id, new_question)

    update.message.reply_text(f"Правильный ответ был: {correct_answer}")
    update.message.reply_text(new_question)

    return ConversationPoints.USER_ANSWER.value


def error(bot, update, error):
    logger.warning("Update '%s' caused error '%s'", update, error)


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Действие отменено",
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main():
    telegram_bot_token = os.environ["TELEGRAM_TOKEN"]

    updater = Updater(token=telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            ConversationPoints.NEW_QUESTION.value:
                [
                    MessageHandler(
                        Filters.regex("^(Новый вопрос)$"),
                        handle_new_question_request
                    )
                ],

            ConversationPoints.USER_ANSWER.value:
                [
                    CommandHandler(
                        "cancel",
                        cancel
                    ),
                    MessageHandler(
                        Filters.regex("^(Сдаться)$"),
                        user_give_up,
                    ),
                    MessageHandler(
                        Filters.text,
                        handle_solution_attempt
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
