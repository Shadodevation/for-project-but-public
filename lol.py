import json as js
import os
import telebot
from telebot import types
cnt = 0
# Замените 'YOUR_TOKEN_HERE' на токен вашего бота
bot = telebot.TeleBot('7488943135:AAGaNFRfMlLFRIjjelZS8bCpi2J-8Dwp6ow')

# Список доступных JSON-файлов
json_dir = 'C:\\Users\\user\\Desktop\\json_test'  # Укажите здесь путь к папке с файлами
if os.path.exists(json_dir) and os.path.isdir(json_dir):
    json_files = [os.path.join(json_dir, f) for f in os.listdir(json_dir) if f.endswith('.json')]
else:
    print(f"Директория {json_dir} не найдена. Проверьте путь.")
    json_files = []

# Загружаем данные из всех JSON-файлов
def load_all_data():
    all_data = []
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = js.load(f)
                if isinstance(data, list):  # Проверяем, что данные являются списком
                    all_data.extend(data)
                else:
                    print(f"Некорректный формат данных в файле {file}. Ожидался список объектов.")
        except (js.JSONDecodeError, IOError) as e:
            print(f"Ошибка чтения файла {file}: {e}")
    return all_data

cars_data = load_all_data()

# Создаем клавиатуру
markup = types.InlineKeyboardMarkup()
button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
markup.add(button_yes, button_no)

# Глобальные переменные для хранения данных
user_data = {}

# Функция для проверки ввода
def validate_input(field, value):
    if field == "volume":
        try:
            volume = float(value)
            return 0.5 <= volume <= 10.0  # Проверка диапазона
        except ValueError:
            return False
    elif field == "year":
        try:
            year = int(value)
            return 1900 <= year <= 2024
        except ValueError:
            return False
    elif field in ["price", "power", "import_price"]:
        try:
            return int(value) > 0
        except ValueError:
            return False
    elif field == "hybrid_type":
        return value.lower() in ["гибрид", "не гибрид"]
    elif field == "vvoz":
        return value.lower() in ["standart", "luxury"]
    else:
        return bool(value)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_bot(message):
    user_data[message.chat.id] = {
        "name": "",
        "volume": "",
        "year": "",
        "price": "",
        "power": "",
        "import_price": "",
        "hybrid_type": "",
        "vvoz": "",
    }
    first_message = f"<b>{message.from_user.first_name}</b>, Проект 11 класса Б, телеграмм бот для поиска автомобилей\nНачнём?"
    bot.send_message(message.chat.id, first_message, parse_mode='html', reply_markup=markup)

# Обработчик текстовых сообщений для ввода данных
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = user_data.get(message.chat.id, None)
    if not user:
        bot.send_message(message.chat.id, "Пожалуйста, начните с команды /start.")
        return

    if not user["name"]:
        user["name"] = message.text
        bot.send_message(message.chat.id, "Название автомобиля принято. Укажите объем (л\u00B3):")
    elif not user["volume"]:
        if validate_input("volume", message.text):
            user["volume"] = message.text
            bot.send_message(message.chat.id, "Объем принят. Укажите год издания:")
        else:
            bot.send_message(message.chat.id, "Некорректный объем. Пожалуйста, введите число в диапазоне 0.5-10.0.")
    elif not user["year"]:
        if validate_input("year", message.text):
            user["year"] = message.text
            bot.send_message(message.chat.id, "Год издания принят. Укажите рыночную цену(рубли):")
        else:
            bot.send_message(message.chat.id, "Некорректный год. Введите значение от 1900 до 2024.")
    elif not user["price"]:
        if validate_input("price", message.text):
            user["price"] = message.text
            bot.send_message(message.chat.id, "Рыночная цена принята. Укажите кватты/лошадиные силы:")
        else:
            bot.send_message(message.chat.id, "Некорректная цена. Введите положительное число.")
    elif not user["power"]:
        if validate_input("power", message.text):
            user["power"] = message.text
            bot.send_message(message.chat.id, "Мощность/лошадиные силы принята. Укажите цену ввоза(рубли):")
        else:
            bot.send_message(message.chat.id, "Некорректная мощность. Введите положительное число.")
    elif not user["import_price"]:
        if validate_input("import_price", message.text):
            user["import_price"] = message.text
            bot.send_message(message.chat.id, "Цена ввоза принята. Укажите тип гибрида (гибрид/не гибрид):")
        else:
            bot.send_message(message.chat.id, "Некорректная цена ввоза. Введите положительное число.")
    elif not user["hybrid_type"]:
        if validate_input("hybrid_type", message.text):
            user["hybrid_type"] = message.text
            bot.send_message(message.chat.id, "Тип гибрида принят. Укажите тип ввоза (standart/luxury):")
        else:
            bot.send_message(message.chat.id, "Некорректный тип гибрида. Введите 'гибрид' или 'не гибрид'.")
    elif not user["vvoz"]:
        if validate_input("vvoz", message.text):
            user["vvoz"] = message.text
            bot.send_message(message.chat.id, "Тип ввоза принят. Ищу совпадения в базе данных...")
            find_matches(message)
        else:
            bot.send_message(message.chat.id, "Некорректный тип ввоза. Введите 'standard' или 'luxury'.")
    else:
        bot.send_message(message.chat.id, "Все данные уже введены. Спасибо!")

# Поиск совпадений в JSON-файлах
def find_matches(message):
    user = user_data.get(message.chat.id, None)
    if not user:
        bot.send_message(message.chat.id, "Пожалуйста, начните с команды /start.")
        return
    cnt = 0
    matches = []
    for car in cars_data:
        if car.get('name', '').lower() == user['name'].lower():
            cnt+=1
        if  str(car.get('volume', '')) == user['volume']:
            cnt+=1
        if str(car.get('year', '')) == user['year']:
            cnt+=1
        if  str(car.get('price', '')) == user['price']:
            cnt+=1
        if str(car.get('power', '')) == user['power']:
            cnt+=1
        if str(car.get('import_price', '')) == user['import_price']:
            cnt+=1
        if car.get('hybrid_type', '').lower() == user['hybrid_type'].lower():
            cnt+=1
        if car.get('vvoz', '').lower() == user['vvoz'].lower():
            cnt+=1
        if cnt >= 2:
            matches.append(car)

    if matches:
        response_message = f"Найдено совпадений: {len(matches)}\n\n"
        for match in matches:
            # Основная информация об автомобиле
            response_message += f"<b>Название:</b> {match.get('name', 'Не указано')}\n"
            response_message += f"<b>Объем:</b> {match.get('volume', 'Не указано')} л\u00B3 \n"
            response_message += f"<b>Год выпуска:</b> {match.get('year', 'Не указан')}\n"
            response_message += f"<b>Цена:</b> {match.get('price', 'Не указана')} руб\n"
            response_message += f"<b>Мощность:</b> {match.get('power', 'Не указана')} л.с.\n"
            response_message += f"<b>Цена ввоза:</b> {match.get('import_price', 'Не указана')} руб\n"
            response_message += f"<b>Тип гибрида:</b> {match.get('hybrid_type', 'Не указан')}\n"
            response_message += f"<b>Тип ввоза:</b> {match.get('vvoz', 'Не указан')}\n"

            # Выравнивание заголовка "Описание" вручную
            response_message += "\n" + " " * 44 + "<b>Описание:</b>\n\n"
            description = match.get('description', 'Нет описания')
            response_message += f"{description}\n"

            # Отправляем фото, если оно указано в JSON
            image_url = match.get('image_url', None)
            if image_url:
                bot.send_photo(message.chat.id, image_url)

        bot.send_message(message.chat.id, response_message, parse_mode='html')
    else:
        bot.send_message(message.chat.id, "Совпадений не найдено в базе данных.")

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def response(call):
    if call.data == "yes":
        bot.send_message(call.message.chat.id, "Введите название автомобиля(На английском):")
    elif call.data == "no":
        bot.send_photo(call.message.chat.id, "https://i.pinimg.com/736x/26/4a/ec/264aec432db8f0a9dfb43c513a4f00d3.jpg")
        bot.send_message(call.message.chat.id, "Если передумаете, нажмите /start.")

# Запуск бота
print("Бот запущен!")
bot.polling()
