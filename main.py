from typing import Dict
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (ApplicationBuilder,
                          MessageHandler,
                          CommandHandler,
                          ContextTypes,
                          filters,
                          ConversationHandler)

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

CHOOSING, INFO = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    ...


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler("start", start)
    app.add_handler(start_handler)
    app.add_handler(MessageHandler(filters.TEXT, echo))

    app.run_polling()


if __name__ == "__main__":
    main()
