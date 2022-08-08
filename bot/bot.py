import os

import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext)
from telegram import Update, ReplyKeyboardMarkup
from dotenv import load_dotenv

from quiz import get_random_question


logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s",
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    reply_keyboard = [["Новый вопрос", "Сдаться"], ["Мой счёт"]]
    greeting_message = "Привет! Я бот для викторин!"

    update.message.reply_text(
        text=greeting_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


def echo(update: Update, context: CallbackContext):
    if update.message.text == "Новый вопрос":
        question = get_random_question()
        update.message.reply_text(question)


def error(bot, update, error):
    logger.warning("Update '%s' caused error '%s'", update, error)


def main():
    load_dotenv()
    telegram_bot_token = os.environ["TELEGRAM_TOKEN"]

    updater = Updater(token=telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, echo))
    
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
