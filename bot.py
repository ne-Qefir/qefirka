import telebot
from telebot import types
import os
from datetime import datetime
from dotenv import load_dotenv
import random

# Загружает переменные из .env
load_dotenv()

# Инициализация бота с использованием переменной окружения
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Словарь для хранения данных пользователя
user_data = {}

# Список для хранения истории
history = []

# Счетчик отправленных сообщений
message_count = 0

# Статистика игр
game_stats = {
    "total_games": 0,
    "wins": 0,
    "losses": 0,
}

# Список поддерживаемых языков программирования
SUPPORTED_LANGUAGES = {
    "python": "🐍 Python",
    "js": "🟨 JavaScript",
    "java": "☕ Java",
    "cpp": "🔵 C++",
    "html": "🌐 HTML",
    "css": "🎨 CSS",
    "php": "🐘 PHP",
    "ruby": "💎 Ruby",
    "go": "🐹 Go",
    "swift": "🐦 Swift",
    "sql": "🗃️ SQL",
    "bash": "🐚 Bash",
    "json": "📄 JSON",
    "xml": "📜 XML",
}

# Папка для сохранения файлов
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("📝 Отправить код")
    btn2 = types.KeyboardButton("📁 Отправить файл")
    btn3 = types.KeyboardButton("📜 История")
    btn4 = types.KeyboardButton("📩 Отправить сообщение")
    btn5 = types.KeyboardButton("ℹ️ Информация")
    btn6 = types.KeyboardButton("🎮 Игры")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    bot.send_message(message.chat.id, "👋 Привет! Выберите действие:", reply_markup=markup)

# Обработчик текстовых сообщений (для кнопок)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global message_count
    if message.text == "📝 Отправить код":
        send_code(message)
    elif message.text == "📁 Отправить файл":
        send_file(message)
    elif message.text == "📜 История":
        show_history(message)
    elif message.text == "📩 Отправить сообщение":
        send_message_to_user(message)
    elif message.text == "ℹ️ Информация":
        get_info(message)
    elif message.text == "🎮 Игры":
        start_game_menu(message)
    else:
        bot.send_message(message.chat.id, "❌ Неизвестная команда. Пожалуйста, используйте кнопки.")

# Обработчик команды /sendcode (через кнопку)
def send_code(message):
    # Запрашиваем язык программирования
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for lang in SUPPORTED_LANGUAGES.values():
        markup.add(lang)
    bot.send_message(message.chat.id, "📝 Выберите язык программирования:", reply_markup=markup)
    bot.register_next_step_handler(message, get_language)

# Функция для получения языка программирования
def get_language(message):
    language = message.text
    if language not in SUPPORTED_LANGUAGES.values():
        bot.send_message(message.chat.id, "❌ Язык не поддерживается. Пожалуйста, выберите язык из списка.")
        return send_code(message)
    user_data[message.chat.id] = {'language': language}
    bot.send_message(message.chat.id, f"✅ Вы выбрали {language}. Теперь введите ваш код:")
    bot.register_next_step_handler(message, get_code)

# Функция для получения кода
def get_code(message):
    global message_count
    code = message.text
    user_data[message.chat.id]['code'] = code
    language = user_data[message.chat.id]['language']
    username = message.from_user.username

    # Формируем сообщение для создателя
    message_to_creator = (
        f"📩 Новый код от пользователя @{username}:\n"
        f"📝 Язык: {language}\n"
        f"💻 Код:\n```{code}```"
    )

    # Отправляем сообщение создателю
    creator_chat_id = os.getenv('CREATOR_CHAT_ID')  # Используем переменную окружения
    bot.send_message(creator_chat_id, message_to_creator, parse_mode="Markdown")
    bot.send_message(message.chat.id, "✅ Ваш код отправлен создателю. Спасибо!")

    # Добавляем запись в историю
    history.append({
        'type': 'code',
        'username': username,
        'language': language,
        'code': code,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Увеличиваем счетчик сообщений
    message_count += 1

# Обработчик команды /sendfile (через кнопку)
def send_file(message):
    bot.send_message(message.chat.id, "📁 Пожалуйста, отправьте файл, который вы хотите переслать создателю.")
    bot.register_next_step_handler(message, handle_file)

# Функция для обработки файла
def handle_file(message):
    global message_count
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Сохраняем файл
        file_name = message.document.file_name
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Отправляем файл создателю
        creator_chat_id = os.getenv('CREATOR_CHAT_ID')  # Используем переменную окружения
        username = message.from_user.username
        bot.send_document(creator_chat_id, open(file_path, 'rb'), caption=f"📁 Файл от @{username}")

        # Уведомляем пользователя
        bot.send_message(message.chat.id, "✅ Ваш файл отправлен создателю. Спасибо!")

        # Добавляем запись в историю
        history.append({
            'type': 'file',
            'username': username,
            'file_name': file_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Увеличиваем счетчик сообщений
        message_count += 1
    else:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправьте файл.")

# Обработчик команды /history (через кнопку)
def show_history(message):
    if not history:
        bot.send_message(message.chat.id, "📜 История пуста.")
        return

    # Формируем сообщение с историей
    history_message = "📜 История отправленных сообщений и файлов:\n\n"
    for entry in history:
        if entry['type'] == 'code':
            history_message += (
                f"📝 Код от @{entry['username']}\n"
                f"📝 Язык: {entry['language']}\n"
                f"🕒 Время: {entry['timestamp']}\n"
                f"💻 Код:\n```{entry['code']}```\n\n"
            )
        elif entry['type'] == 'file':
            history_message += (
                f"📁 Файл от @{entry['username']}\n"
                f"📄 Имя файла: {entry['file_name']}\n"
                f"🕒 Время: {entry['timestamp']}\n\n"
            )

    bot.send_message(message.chat.id, history_message, parse_mode="Markdown")

# Обработчик команды /sendmessage (через кнопку)
def send_message_to_user(message):
    if str(message.chat.id) != os.getenv('CREATOR_CHAT_ID'):
        bot.send_message(message.chat.id, "❌ Эта команда доступна только создателю.")
        return

    bot.send_message(message.chat.id, "📩 Введите username пользователя, которому хотите отправить сообщение:")
    bot.register_next_step_handler(message, get_username_for_message)

def get_username_for_message(message):
    username = message.text
    if not username.startswith('@'):
        username = '@' + username
    user_data[message.chat.id] = {'username': username}
    bot.send_message(message.chat.id, f"📝 Введите сообщение для пользователя {username}:")
    bot.register_next_step_handler(message, get_message_for_user)

def get_message_for_user(message):
    global message_count
    user_message = message.text
    username = user_data[message.chat.id]['username']
    bot.send_message(message.chat.id, f"✅ Сообщение отправлено пользователю {username}.")
    bot.send_message(username, f"📩 Сообщение от создателя:\n{user_message}")

    # Увеличиваем счетчик сообщений
    message_count += 1

# Обработчик команды /getinfo (через кнопку)
def get_info(message):
    global message_count, game_stats
    win_rate = (game_stats["wins"] / game_stats["total_games"] * 100) if game_stats["total_games"] > 0 else 0
    info_message = (
        f"ℹ️ Информация:\n"
        f"📊 Количество отправленных сообщений: {message_count}\n"
        f"🎮 Количество сыгранных игр: {game_stats['total_games']}\n"
        f"🏆 Количество побед: {game_stats['wins']}\n"
        f"💀 Количество поражений: {game_stats['losses']}\n"
        f"📈 Средний процент побед: {win_rate:.2f}%"
    )
    bot.send_message(message.chat.id, info_message)

# Обработчик команды 🎮 Игры
def start_game_menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("🎮 Крестики-нолики", callback_data="start_tic_tac_toe")
    markup.add(btn1)
    bot.send_message(message.chat.id, "🎮 Выберите игру:", reply_markup=markup)

# Обработчик inline-кнопок
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == "start_tic_tac_toe":
        start_tic_tac_toe(call.message)
    elif call.data.startswith("ttt_"):
        process_tic_tac_toe(call)
    elif call.data == "exit_game":
        start(call.message)

# Функция для начала игры в крестики-нолики
def start_tic_tac_toe(message):
    # Инициализация игрового поля
    user_data[message.chat.id] = {
        "board": [" " for _ in range(9)],
        "player": "X",
        "bot": "O",
        "game_over": False,
    }
    show_tic_tac_toe_board(message)

# Функция для отображения игрового поля
def show_tic_tac_toe_board(message):
    board = user_data[message.chat.id]["board"]
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Добавляем кнопки рядами по три
    for i in range(0, 9, 3):
        row = [
            types.InlineKeyboardButton(board[i], callback_data=f"ttt_{i}"),
            types.InlineKeyboardButton(board[i+1], callback_data=f"ttt_{i+1}"),
            types.InlineKeyboardButton(board[i+2], callback_data=f"ttt_{i+2}")
        ]
        markup.add(*row)
    
    # Добавляем кнопку выхода
    exit_btn = types.InlineKeyboardButton("🚪 Выйти", callback_data="exit_game")
    markup.add(exit_btn)
    
    bot.send_message(message.chat.id, "🎮 Крестики-нолики. Ваш ход (X):", reply_markup=markup)

# Функция для обработки хода в крестики-нолики
def process_tic_tac_toe(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data.split("_")[1]
    index = int(data)

    if user_data.get(chat_id, {}).get("game_over", True):
        bot.answer_callback_query(call.id, "Игра завершена. Начните новую игру.")
        return

    board = user_data[chat_id]["board"]
    if board[index] != " ":
        bot.answer_callback_query(call.id, "Эта клетка уже занята!")
        return

    # Ход игрока
    board[index] = user_data[chat_id]["player"]
    if check_winner(board, user_data[chat_id]["player"]):
        user_data[chat_id]["game_over"] = True
        game_stats["total_games"] += 1
        game_stats["wins"] += 1
        bot.edit_message_text("🎉 Вы выиграли!", chat_id, call.message.message_id)
        return

    if " " not in board:
        user_data[chat_id]["game_over"] = True
        game_stats["total_games"] += 1
        bot.edit_message_text("🤝 Ничья!", chat_id, call.message.message_id)
        return

    # Ход бота
    bot_move = get_bot_move(board)
    board[bot_move] = user_data[chat_id]["bot"]
    if check_winner(board, user_data[chat_id]["bot"]):
        user_data[chat_id]["game_over"] = True
        game_stats["total_games"] += 1
        game_stats["losses"] += 1
        bot.edit_message_text("🤖 Бот выиграл!", chat_id, call.message.message_id)
        return

    show_tic_tac_toe_board(call.message)

# Функция для проверки победителя
def check_winner(board, player):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Горизонтальные
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Вертикальные
        [0, 4, 8], [2, 4, 6]              # Диагональные
    ]
    for combo in winning_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] == player:
            return True
    return False

# Функция для хода бота
def get_bot_move(board):
    empty_cells = [i for i, cell in enumerate(board) if cell == " "]
    return random.choice(empty_cells)

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
