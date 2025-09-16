import os 
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup
from gpt import *
from util import *

load_dotenv()


async def gpt(update, context):
    dialog.mode = "gpt"
    text = load_message("gpt")
    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def gpt_dialog(update, context):
    text = update.message.text
    prompt = load_message("gpt")
    answer = await chatgpt.send_question(prompt, text)
    await send_text(update, context, answer)


async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text, {
        "date_grande":"Ариана Гранде",
        "date_robbie":"Марго Робби",
        "date_zendaya":"Зендея",
        "date_gosling":"Райан Гослинг",
        "date_hardy":"Том Харди"
    })


async def date_dialog(update, context):
    text = update.message.text
    my_message = await send_text(update, context, "Печатает...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)


async def date_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    await send_photo(update, context, query)
    await send_text(update, context, "Отличный выбор! Пригласите парня (девушку) на свидание за 5 сообщений. Удачи!")
    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def start(update, context):
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        "start": "Запустить бота",
        "gpt": "Начать диалог с ChatGPT",
        "profile": "Сгенерировать профиль",
        "opener":"Сгенерировать первое сообщение для знакомства",
        "date": "Начать диалог со звездой",
        "message":"Сгенерировать следующее сообщение"
    })
    # contact_button = KeyboardButton("Отправить номер телефона", request_contact=True)
    # location_button = KeyboardButton("Отправить местоположение", request_location=True)

    # reply_markup = ReplyKeyboardMarkup(
    #     [[contact_button], [location_button]],
    #     resize_keyboard=True,
    #     one_time_keyboard=True
    # )

    # await update.message.reply_text(
    #     "Привет! Пожалуйста, отправьте свой номер телефона или местоположение:",
    #     reply_markup=reply_markup
    # )


async def hello(update, context):
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    if dialog.mode == "date":
        await date_dialog(update, context)
    if dialog.mode == "message":
        await message_dialog(update, context)
    if dialog.mode == "profile":
        await profile_dialog(update, context)
    if dialog.mode == "opener":
        await opener_dialog(update, context)
    print(update.effective_user.username + ": " + update.message.text)
    # await send_photo(update, context, "avatar_main")
    # await send_text_buttons(update, context, "Запустить процесс?", {
    #     "start":"Запустить",
    #     "stop":"Остановить"
    # })


# async def hello_button(update, context):
#     query = update.callback_query.data
    # if query == "start":
    #     await send_text(update, context, "Процесс запущен")
    #     print("user " + update.effective_user.username + " clicked start")
    # else:
    #     await send_text(update, context, "Процесс остановлен")
    #     print(f"user " + update.effective_user.username + " clicked stop")


async def message(update, context):
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next":"Сгенерировать следующее сообщение",
        "message_date":"Сгенерировать приглашение на свидание"
    })


async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)


async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()
    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update, context, "Анализирую...")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)
    dialog.list.clear()

async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Сколько вам лет?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Кем вы работаете?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "У вас есть хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Что вам не нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text 
        await send_text(update, context, "Какие у вас цели знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(update, context, "Анализиую...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update, context):
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)
    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Имя вашего партнера?")


async def opener_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ему (ей) лет?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцените его (ее) внешность: 1-10 баллов")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Кем он (она) работает?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text 
        await send_text(update, context, "Ваши цели знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        answer = await chatgpt.send_question(prompt, user_info)
        await send_text(update, context, answer)


async def handle_location(update, context):
    location = update.message.location
    print(update.effective_user.username + ": " + location)


async def handle_contact(update, context):
    contact = update.message.contact
    print(contact)


async def log_all_commands(update, context):
    command = update.message.text
    username = update.effective_user.username or "Unknown"
    print(f"{username} used command: {command}")

dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

chatgpt_token = os.getenv('CHATGPT_TOKEN')
chatgpt = ChatGptService(token=chatgpt_token)

app_token=os.getenv('APP_TOKEN')
app = ApplicationBuilder().token(app_token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("opener", opener))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(MessageHandler(filters.COMMAND, log_all_commands), group=1)
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
app.add_handler(MessageHandler(filters.LOCATION, handle_location))

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
# app.add_handler(CallbackQueryHandler(hello_button))

app.run_polling()
