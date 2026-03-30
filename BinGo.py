import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = "8474449455:AAHt1fWysYAWGjFUYac4j_aRdHZrN-k-Ge8"
ADMIN_ID =  5128613422  # Замените на Telegram ID администратора

# --- Клавиатуры ---
lang_keyboard = [["Русский", "English"]]
main_menu_keyboard_ru = [["📦 Создать заказ", "📋 Мои заказы"],
                         ["💰 Тарифы", "📜 Правила"],
                         ["👨‍💻 Связаться с оператором"]]

main_menu_keyboard_en = [["📦 Create order", "📋 My orders"],
                         ["💰 Tariffs", "📜 Rules"],
                         ["👨‍💻 Contact operator"]]

main_menu_markup_ru = ReplyKeyboardMarkup(main_menu_keyboard_ru, resize_keyboard=True)
main_menu_markup_en = ReplyKeyboardMarkup(main_menu_keyboard_en, resize_keyboard=True)

order_types_keyboard_ru = [["🍔 Urban Buns", "Купить и привезти"], ["Забрать и отвезти", "Другое"]]
order_types_keyboard_en = [["🍔 Urban Buns", "Buy and deliver"], ["Pick up and deliver", "Other"]]

order_types_markup_ru = ReplyKeyboardMarkup(order_types_keyboard_ru, resize_keyboard=True)
order_types_markup_en = ReplyKeyboardMarkup(order_types_keyboard_en, resize_keyboard=True)
confirm_keyboard_ru = [["✅ Подтвердить", "✏ Изменить", "❌ Отменить"]]
confirm_keyboard_en = [["✅ Confirm", "✏ Change", "❌ Cancel"]]

confirm_markup_ru = ReplyKeyboardMarkup(confirm_keyboard_ru, resize_keyboard=True)
confirm_markup_en = ReplyKeyboardMarkup(confirm_keyboard_en, resize_keyboard=True)

lang_markup = ReplyKeyboardMarkup(lang_keyboard, resize_keyboard=True)
# --- Тексты на двух языках ---
TEXTS = {
    "Русский": {
        "choose_lang": "Привет! 👋 Выберите язык:",
        "main_menu": "🏠 Главное меню:",
        "create_order": "📦 Создать заказ",
        "my_orders": "📋 Мои заказы",
        "tariffs": "💰 Тарифы",
        "rules": "📜 Правила",
        "contact_operator": "👨‍💻 Связаться с оператором",
        "order_type": "📦 Выберите тип заказа:",
        "order_description": "📝 Опишите ваш заказ (что нужно купить/доставить):",
        "order_address": "📍 Введите адрес доставки:",
        "order_time": "⏰ Укажите время доставки:",
        "contact_name": "👤Введите ваше имя:",
        "contact_phone": "📞Введите ваш телефон:",
        "comment": "💬Комментарий к заказу (необязательно):",
        "confirm": "✅ Подтвердить",
        "change": "✏️ Изменить",
        "cancel": "❌ Отменить",
        "order_accepted": "✅ Заказ принят!\n📦 Номер: #{id}\n📊 Статус: Новый",
        "invalid_option": "Пожалуйста, выберите вариант из меню.",
        "my_orders_empty": "У вас пока нет заказов.",
        "tariffs_text": "💰 Тарифы:\n🍔 Urban Buns — Бесплатно\n🚲 Велодоставка — от 4€\n🚗 Машина — от 6€\n⚙️ Сложные поручения — по договорённости",
        "rules_text": "📜 Правила:\n- ✅ Только легальные товары\n- ❌ Запрещены наркотики и оружие\n- 🔍 Курьер может уточнить заказ\n- 🚫 Сервис может отказать",
        "contact_admin": "📩 Напишите админу: @mrjkie"
    },
    "English": {
        "choose_lang": "Hello! 👋 Choose language:",
        "main_menu": "🏠 Main menu:",
        "create_order": "📦 Create order",
        "my_orders": "📋 My orders",
        "tariffs": "💰 Tariffs",
        "rules": "📜 Rules",
        "contact_operator": "👨‍💻 Contact operator",
        "order_type": "📦 Select order type:",
        "order_description": "📝 Describe your order (what to buy/deliver):",
        "order_address": "📍 Enter delivery address or send location:",
        "order_time": "⏰ Delivery time:\n1. As soon as possible\n2. Specify time",
        "contact_name": "👤 Enter your name:",
        "contact_phone": "📞 Enter your phone:",
        "comment": "💬 Comment (optional):",
        "confirm": "✅ Confirm",
        "change": "✏ Change",
        "cancel": "❌ Cancel",
        "order_accepted": "Your order is accepted ✅\n📦 Order number: #{id}\n📊 Status: New",
        "invalid_option": "Please choose an option from the menu.",
        "my_orders_empty": "You have no orders yet.",
        "tariffs_text": "💰 Tariffs:\n🍔 Urban Buns — Free\n🚲 Bike delivery — from 4€\n🚗 Car delivery — from 6€\n⚙ Complex tasks — by agreement",
        "rules_text": "📜 Rules:\n- ✅ Only legal goods are delivered\n- ❌ Drugs, weapons, and other prohibited items are forbidden\n- 🔍 The courier has the right to check order contents\n- 🚫 The service has the right to refuse suspicious orders",
        "contact_admin": "📩 Send a message to the admin: @mrjkie"
    }
}

# --- База данных ---
conn = sqlite3.connect("bingo.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    language TEXT,
    type TEXT,
    description TEXT,
    address TEXT,
    time TEXT,
    name TEXT,
    phone TEXT,
    comment TEXT,
    status TEXT,
    created_at TEXT
)
""")
conn.commit()

# --- Старт / выбор языка ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTS["Русский"]["choose_lang"], reply_markup=lang_markup)
    context.user_data.clear()
    context.user_data["stage"] = "lang"

# --- Обработка сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    stage = context.user_data.get("stage", "")

    # Получаем язык пользователя, если он выбран, иначе по умолчанию Русский
    lang = context.user_data.get("language", "Русский")
    
    # --- Выбор языка ---
    if stage == "lang":
        if text not in ["Русский", "English"]:
            await update.message.reply_text("Пожалуйста, выберите язык!", reply_markup=lang_markup)
            return

        context.user_data["language"] = text
        context.user_data["user_id"] = update.message.from_user.id
        context.user_data["username"] = update.message.from_user.username or "Нет username"
        context.user_data["stage"] = "main_menu"

        # Выбираем нужную клавиатуру
        if text == "Русский":
            menu_markup = main_menu_markup_ru
            msg = "Вы выбрали язык: Русский"
        else:
            menu_markup = main_menu_markup_en
            msg = "You chose language: English"

        await update.message.reply_text(msg, reply_markup=menu_markup)
        return

    # --- Главное меню ---
    if stage == "main_menu":
        menu_markup = main_menu_markup_ru if lang == "Русский" else main_menu_markup_en
        if text == TEXTS[lang]["create_order"]:
            context.user_data["stage"] = "order_type"
            # Выбираем клавиатуру в зависимости от языка
            markup = order_types_markup_ru if lang == "Русский" else order_types_markup_en
            await update.message.reply_text(TEXTS[lang]["order_type"], reply_markup=markup)
        elif text == TEXTS[lang]["my_orders"]:
            user_id = update.message.from_user.id
            cursor.execute("SELECT id, type, status, created_at FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5", (user_id,))
            orders = cursor.fetchall()
            if orders:
                msg = "Ваши заказы:\n" + "\n".join([f"#{o[0]} | {o[1]} | {o[2]} | {o[3]}" for o in orders])
            else:
                msg = TEXTS[lang]["my_orders_empty"]
            await update.message.reply_text(msg, reply_markup=menu_markup)
        elif text == TEXTS[lang]["tariffs"]:
            await update.message.reply_text(TEXTS[lang]["tariffs_text"], reply_markup=menu_markup)
        elif text == TEXTS[lang]["rules"]:
            await update.message.reply_text(TEXTS[lang]["rules_text"], reply_markup=menu_markup)
        elif text == TEXTS[lang]["contact_operator"]:
            await update.message.reply_text(TEXTS[lang]["contact_admin"], reply_markup=menu_markup)
        else:
            await update.message.reply_text(TEXTS[lang]["invalid_option"], reply_markup=menu_markup)
        return

    # --- Выбор типа заказа ---
    if stage == "order_type":
        markup = order_types_markup_ru if lang == "Русский" else order_types_markup_en
        valid_options = [item for row in (order_types_keyboard_ru if lang == "Русский" else order_types_keyboard_en) for item in row]

        if text not in valid_options:
            await update.message.reply_text(TEXTS[lang]["order_type"], reply_markup=markup)
            return

        context.user_data["order_type"] = text
        context.user_data["stage"] = "order_description"
        await update.message.reply_text(TEXTS[lang]["order_description"], reply_markup=None)

    # --- Описание заказа ---
    if stage == "order_description":
        context.user_data["description"] = text
        context.user_data["stage"] = "order_address"
        await update.message.reply_text(TEXTS[lang]["order_address"])
        return

    # --- Адрес ---
    if stage == "order_address":
        context.user_data["address"] = text
        context.user_data["stage"] = "order_time"
        await update.message.reply_text(TEXTS[lang]["order_time"])
        return

    # --- Время ---
    if stage == "order_time":
        if text.lower() in ["как можно скорее", "as soon as possible"]:
            context.user_data["time"] = text
        else:
            context.user_data["time"] = text
        context.user_data["stage"] = "order_contact_name"
        await update.message.reply_text(TEXTS[lang]["contact_name"])
        return

    # --- Имя ---
    if stage == "order_contact_name":
        context.user_data["name"] = text
        context.user_data["stage"] = "order_contact_phone"
        await update.message.reply_text(TEXTS[lang]["contact_phone"])
        return

    # --- Телефон ---
    if stage == "order_contact_phone":
        context.user_data["phone"] = text
        context.user_data["stage"] = "order_comment"
        await update.message.reply_text(TEXTS[lang]["comment"])
        return

    # --- Комментарий ---
    if stage == "order_comment":
        context.user_data["comment"] = text
        # --- Подтверждение ---
        order_summary = (
            f"📦 Ваш заказ:\n"
            f"📋 Тип заказа: {context.user_data['order_type']}\n"
            f"📝 Описание: {context.user_data['description']}\n"
            f"📍 Адрес: {context.user_data['address']}\n"
            f"⏰ Время: {context.user_data['time']}\n"
            f"👤 Имя: {context.user_data['name']}\n"
            f"📞 Телефон: {context.user_data['phone']}\n"
            f"💬 Комментарий: {context.user_data['comment']}"
        )
        context.user_data["stage"] = "order_confirm"
        await update.message.reply_text(order_summary, reply_markup=confirm_markup)
        return

    # --- Подтверждение заказа ---
    if stage == "order_confirm":
        markup = confirm_markup_ru if lang == "Русский" else confirm_markup_en
        if text == TEXTS[lang]["confirm"]:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Сохраняем заказ в базе
            cursor.execute("""
                INSERT INTO orders (user_id, username, language, type, description, address, time, name, phone, comment, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                context.user_data["user_id"],
                context.user_data["username"],
                lang,
                context.user_data["order_type"],
                context.user_data["description"],
                context.user_data["address"],
                context.user_data["time"],
                context.user_data.get("name", ""),
                context.user_data.get("phone", ""),
                context.user_data.get("comment", ""),
                "Новый" if lang == "Русский" else "New",
                now
            ))
            conn.commit()
            order_id = cursor.lastrowid

            # --- Уведомление заказчику ---
            await update.message.reply_text(TEXTS[lang]["order_accepted"].format(id=order_id), reply_markup=main_menu_markup)

            # --- Уведомление админу ---
            admin_message = (
                f"📦 Новый заказ #{order_id}\n\n"
                f"👤 Пользователь: {context.user_data['username']} ({context.user_data['user_id']})\n"
                f"📋 Тип: {context.user_data['order_type']}\n"
                f"📝 Описание: {context.user_data['description']}\n"
                f"📍 Адрес: {context.user_data['address']}\n"
                f"⏰ Время: {context.user_data['time']}\n"
                f"📞 Телефон: {context.user_data.get('phone','')}\n"
                f"💬 Комментарий: {context.user_data.get('comment','')}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

        elif text == TEXTS[lang]["change"]:
            context.user_data["stage"] = "order_description"
            await update.message.reply_text(TEXTS[lang]["order_description"], reply_markup=None)
        elif text == TEXTS[lang]["cancel"]:
            await update.message.reply_text("Заказ отменён.", reply_markup=main_menu_markup)
            context.user_data["stage"] = "main_menu"
        else:
            await update.message.reply_text("Выберите действие:", reply_markup=confirm_markup)
        return

# --- Запуск бота ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()
