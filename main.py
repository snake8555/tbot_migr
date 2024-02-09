import os
from typing import Dict

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

load_dotenv()

TOKEN = os.getenv("TOKEN")

CHOOSING, CLOSE, INPUT = range(3)

reply_keyboard = [
    ["Check judge", "INFO"],
    ["Done"],
]

reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Этот бот создан для помощи в поиске разной имиграционной информации. "
        "Сейчас бот находится в стадии разработки и со времением будет дополнтся.",
        reply_markup=reply_markup
    )
    return CHOOSING

async def check_judge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text("Input name Judge")
    return INPUT

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Этот раздел пока в разработке",
                                    reply_markup=reply_markup)
    return CHOOSING

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    await update.message.reply_text("Для вызова меню введите /start",
                                    reply_markup=ReplyKeyboardRemove())
    user_data.clear()
    return ConversationHandler.END

async def unknow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Я пока не понимаю другие комманды.\nВведите /start")


async def input_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text = update.message.text
    category = user_data["choice"]
    user_data[category] = text
    del user_data["choice"]

    await update.message.reply_text(text, reply_markup=reply_markup)
    return CHOOSING

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Check judge)$"), check_judge
                ),
                MessageHandler(
                    filters.Regex("^(INFO)$"), info
                )
            ],
            CLOSE: [
                MessageHandler(
                    filters.Regex("^(Done)$"), done
                )
            ],
            INPUT: [
                MessageHandler(
                    filters.TEXT, input_text
                )
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), done)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND), unknow_cmd))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
