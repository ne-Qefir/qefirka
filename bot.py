import telebot
from telebot import types
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружает переменные из .env
load_dotenv()

# Инициализация бота с использованием переменной окружения
bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

# Словарь для хранения данных пользователя
user_data = {}

# Список для хранения истории
history = []

# Список поддерживаемых языков программирования
SUPPORTED_LANGUAGES = {
    "python": "Python",
    "js": "JavaScript",
    "java": "Java",
    "cpp": "C++",
    "html": "HTML",
    "css": "CSS",
    "php": "PHP",
    "ruby": "Ruby",
    "go": "Go",
    "swift": "Swift",
    "sql": "SQL",
    "bash": "Bash",
    "json": "JSON",
    "xml": "XML",
}

# Папка для сохранения файлов
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Функция для создания клавиатуры с кнопками
def create_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("/sendcode")
    btn2 = types.KeyboardButton("/sendfile")
    btn3 = types.KeyboardButton("/history")
    btn4 = types.KeyboardButton("/sendmessage")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выберите команду:", reply_markup=create_keyboard())

# Обработчик команды /sendcode
@bot.message_handler(commands=['sendcode'])
def send_code(message):
    # Запрашиваем язык программирования
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for lang in SUPPORTED_LANGUAGES.values():
        markup.add(lang)
    bot.send_message(message.chat.id, "Выберите язык программирования:", reply_markup=markup)
    bot.register_next_step_handler(message, get_language)

# Функция для получения языка программирования
def get_language(message):
    language = message.text
    if language not in SUPPORTED_LANGUAGES.values():
        bot.send_message(message.chat.id, "Язык не поддерживается. Пожалуйста, выберите язык из списка.")
        return send_code(message)
    user_data[message.chat.id] = {'language': language}
    bot.send_message(message.chat.id, f"Вы выбрали {language}. Теперь введите ваш код:")
    bot.register_next_step_handler(message, get_code)

# Функция для получения кода
def get_code(message):
    code = message.text
    user_data[message.chat.id]['code'] = code
    language = user_data[message.chat.id]['language']
    username = message.from_user.username

    # Формируем сообщение для создателя
    message_to_creator = (
        f"Новый код от пользователя @{username}:\n"
        f"Язык: {language}\n"
        f"Код:\n```{code}```"
    )

    # Отправляем сообщение создателю
    creator_chat_id = os.getenv('CREATOR_CHAT_ID')  # Используем переменную окружения
    bot.send_message(creator_chat_id, message_to_creator, parse_mode="Markdown")
    bot.send_message(message.chat.id, "Ваш код отправлен создателю. Спасибо!", reply_markup=create_keyboard())

    # Добавляем запись в историю
    history.append({
        'type': 'code',
        'username': username,
        'language': language,
        'code': code,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

# Обработчик команды /sendfile
@bot.message_handler(commands=['sendfile'])
def send_file(message):
    bot.send_message(message.chat.id, "Пожалуйста, отправьте файл, который вы хотите переслать создателю.")
    bot.register_next_step_handler(message, handle_file)

# Функция для обработки файла
def handle_file(message):
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
        bot.send_document(creator_chat_id, open(file_path, 'rb'), caption=f"Файл от @{username}")

        # Уведомляем пользователя
        bot.send_message(message.chat.id, "Ваш файл отправлен создателю. Спасибо!", reply_markup=create_keyboard())

        # Добавляем запись в историю
        history.append({
            'type': 'file',
            'username': username,
            'file_name': file_name,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте файл.", reply_markup=create_keyboard())

# Обработчик команды /history
@bot.message_handler(commands=['history'])
def show_history(message):
    if not history:
        bot.send_message(message.chat.id, "История пуста.", reply_markup=create_keyboard())
        return

    # Формируем сообщение с историей
    history_message = "История отправленных сообщений и файлов:\n\n"
    for entry in history:
        if entry['type'] == 'code':
            history_message += (
                f"📝 Код от @{entry['username']}\n"
                f"Язык: {entry['language']}\n"
                f"Время: {entry['timestamp']}\n"
                f"Код:\n```{entry['code']}```\n\n"
            )
        elif entry['type'] == 'file':
            history_message += (
                f"📁 Файл от @{entry['username']}\n"
                f"Имя файла: {entry['file_name']}\n"
                f"Время: {entry['timestamp']}\n\n"
            )

    bot.send_message(message.chat.id, history_message, parse_mode="Markdown", reply_markup=create_keyboard())

# Обработчик команды /sendmessage
@bot.message_handler(commands=['sendmessage'])
def send_message_command(message):
    bot.send_message(message.chat.id, "Введите сообщение, которое вы хотите отправить создателю:")
    bot.register_next_step_handler(message, handle_send_message)

# Функция для обработки сообщения
def handle_send_message(message):
    user_message = message.text
    username = message.from_user.username
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Формируем сообщение для создателя
    message_to_creator = (
        f"Новое сообщение от пользователя @{username}:\n"
        f"Время: {timestamp}\n"
        f"Сообщение:\n{user_message}"
    )

    # Отправляем сообщение создателю
    creator_chat_id = os.getenv('CREATOR_CHAT_ID')  # Используем переменную окружения
    bot.send_message(creator_chat_id, message_to_creator)
    bot.send_message(message.chat.id, "Ваше сообщение отправлено создателю. Спасибо!", reply_markup=create_keyboard())

    # Добавляем запись в историю
    history.append({
        'type': 'message',
        'username': username,
        'message': user_message,
        'timestamp': timestamp
    })

# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)
