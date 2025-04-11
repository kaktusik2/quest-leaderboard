import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Питання і відповіді зчитуються з JSON-файлу
QUESTIONS_FILE = "questions.json"
STATS_FILE = "stats.json"

# Завантаження питань
def load_questions():
    with open(QUESTIONS_FILE, "r") as file:
        return json.load(file)

# Завантаження статистики
def load_stats():
    try:
        with open(STATS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Збереження статистики
def save_stats(stats):
    with open(STATS_FILE, "w") as file:
        json.dump(stats, file)

# Питання для користувача
def ask_question(update: Update, context: CallbackContext) -> None:
    questions = load_questions()
    user_id = str(update.effective_user.id)
    
    # Вибір питання
    if "question_index" not in context.user_data:
        context.user_data["question_index"] = 0
        context.user_data["correct_answers"] = 0

    question_index = context.user_data["question_index"]
    if question_index >= len(questions):
        update.message.reply_text(f"Ви завершили квест! Правильних відповідей: {context.user_data['correct_answers']}.")
        save_stats_to_global(update.effective_user.first_name, context.user_data["correct_answers"])
        return

    question = questions[question_index]
    keyboard = [
        [InlineKeyboardButton(option, callback_data=str(i)) for i, option in enumerate(question["options"])]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(question["question"], reply_markup=reply_markup)

# Обробник натискання кнопок
def handle_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    user_id = str(query.from_user.id)
    questions = load_questions()
    question_index = context.user_data["question_index"]

    # Перевірка правильної відповіді
    correct_index = questions[question_index]["correct"]
    if int(query.data) == correct_index:
        context.user_data["correct_answers"] += 1
        query.edit_message_text(text="Правильна відповідь!")
    else:
        query.edit_message_text(text="Неправильна відповідь.")

    # Перехід до наступного питання
    context.user_data["question_index"] += 1
    ask_question(query, context)

# Збереження статистики до глобальної таблиці
def save_stats_to_global(username, correct_answers):
    stats = load_stats()
    stats[username] = max(stats.get(username, 0), correct_answers)
    save_stats(stats)

# Показ таблиці лідерів
def show_leaders(update: Update, context: CallbackContext) -> None:
    stats = load_stats()
    leaderboard = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    message = "Таблиця лідерів:\n"
    for username, score in leaderboard:
        message += f"{username}: {score} правильних відповідей\n"
    update.message.reply_text(message)

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Ласкаво просимо до квесту! Почнемо!")
    ask_question(update, context)

def main():
    updater = Updater("7885400830:AAEqh9FkCyCX-VhM8Xn-gVRZcfKXIIV2Em8")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("leaders", show_leaders))
    dispatcher.add_handler(CallbackQueryHandler(handle_answer))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
