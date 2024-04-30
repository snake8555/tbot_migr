import os
from typing import Dict
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)
from parsing import search_name

load_dotenv()

TOKEN = os.getenv("TOKEN")

CHOOSING, CLOSE, INPUT = range(3)

ADM_PWD = ""

reply_keyboard = [
    ["Проверка судьи", "INFO"],
    ["Done"],
]

adm_kb = [
    ["command 1", 'command 2'],
    ["close admin panel"]
]

reply_markup = ReplyKeyboardMarkup(
    reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
reply_adm = ReplyKeyboardMarkup(
    adm_kb, one_time_keyboard=True, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Привет! Этот бот создан для помощи в поиске разной "
        "иммиграционной информации. Сейчас бот находится в стадии "
        "разработки и со временем будет дополнятся.",
        reply_markup=reply_markup
    )
    return CHOOSING


async def check_judge(update: Update,
                      context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    context.user_data["choice"] = text
    await update.message.reply_text("Введите имя судьи")
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


async def unknow_cmd(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Я пока не понимаю другие "
                                    "комманды.\nВведите /start",
                                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def input_text(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    text: str = update.message.text
    if not text.isalpha() or len(text) < 2:
        await update.message.reply_text("Имя не может быть меньше 3 символов и"
                                        " содержать цифры или символы.")
        return INPUT

    category = user_data["choice"]
    user_data[category] = text
    if "choice" in user_data:
        del user_data["choice"]

    lst = search_name(f"{text}")
    res = ""
    if len(lst) == 0:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Проверте имя/фамилию или судьи еще нет в базе",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        for i in range(len(lst)):
            for j in lst[i]:
                res += f"{j}\n"
            res += "\n"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=res,
            reply_markup=ReplyKeyboardRemove()
        )
    user_data.clear()
    return ConversationHandler.END


# async def chk_pwd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     if ADM_PWD == "":
#         await....


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if ADM_PWD == "":
        await update.message.reply_text(
            text="Установите пароль администратора.")
        return INPUT
    else:
        await update.message.reply_text(text="Введите пароль администратора")
        return INPUT


async def check_pass(update: Update,
                     context: ContextTypes.DEFAULT_TYPE) -> int:
    global ADM_PWD
    text = update.message.text
    context.user_data["password"] = text
    if ADM_PWD == "":
        ADM_PWD = text
        await update.message.reply_text("Password created.")
        return ConversationHandler.END
    elif ADM_PWD == text:
        await update.message.reply_text(text="Acceess.",
                                        reply_markup=reply_adm)
        return CHOOSING
    else:
        await update.message.reply_text("Pasword Error")
        return ConversationHandler.END


async def close_adm_panel(update: Update,
                          context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Panel closed")
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(Проверка судьи)$"), check_judge
                ),
                MessageHandler(
                    filters.Regex("^(INFO)$"), info
                ),
                MessageHandler(
                    filters.TEXT, unknow_cmd
                ),
                MessageHandler(
                    filters.Regex("^(Done)$"), done
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

    conv_handler_adm = ConversationHandler(
        entry_points=[CommandHandler("admin", admin)],
        states={
            CHOOSING: [
                MessageHandler(
                    filters.Regex("^(close)$"), done
                ),
            ],
            CLOSE: [
                MessageHandler(
                    filters.Regex("^(done)$"), done
                )
            ],
            INPUT: [
                MessageHandler(
                    filters.TEXT, check_pass
                ),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^(Done)$"), done)],
    )

    app.add_handler(conv_handler)
    app.add_handler(conv_handler_adm)
    app.add_handler(CommandHandler("done", done))
    app.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND),
                                   unknow_cmd))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    print("GO!")
    main()
