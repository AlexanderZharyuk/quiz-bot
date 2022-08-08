import os

import logging

from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, CallbackContext)
from telegram import Update
from dotenv import load_dotenv


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def echo(update: Update, context: CallbackContext):
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    load_dotenv()
    telegram_bot_token = os.environ['TELEGRAM_TOKEN']

    updater = Updater(token=telegram_bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
