import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

TOKEN = "8474449455:AAHt1fWysYAWGjFUYac4j_aRdHZrN-k-Ge8"
ADMIN_ID =  5128613422  # Замените на Telegram ID администратора

# --- Клавиатуры ---
lang_keyboard = [["Русский", "English", "Eesti"]]
main_menu_keyboard_ru = [["📦 Создать заказ", "📋 Мои заказы"],
                         ["💰 Тарифы", "📜 Правила"],
                         ["👨‍💻 Связаться с оператором"]]

main_menu_keyboard_en = [["📦 Create order", "📋 My orders"],
                         ["💰 Tariffs", "📜 Rules"],
                         ["👨‍💻 Contact operator"]]

main_menu_keyboard_ee = [["📦 Loo tellimus", "📋 Minu tellimused"],
                         ["💰 Hinnad", "📜 Reeglid"],
                         ["👨‍💻 Võta ühendust operaatoriga"]]



main_menu_markup_ee = ReplyKeyboardMarkup(main_menu_keyboard_ee, resize_keyboard=True)
main_menu_markup_ru = ReplyKeyboardMarkup(main_menu_keyboard_ru, resize_keyboard=True)
main_menu_markup_en = ReplyKeyboardMarkup(main_menu_keyboard_en, resize_keyboard=True)

order_types_keyboard_ru = [["🍔 Urban Buns", "Купить и привезти"], ["Забрать и отвезти", "Другое"]]
order_types_keyboard_en = [["🍔 Urban Buns", "Buy and deliver"], ["Pick up and deliver", "Other"]]
order_types_keyboard_ee = [["🍔 Urban Buns", "Osta ja too"], ["Võta peale ja vii kohale", "Muu"]]

order_types_markup_ee = ReplyKeyboardMarkup(order_types_keyboard_ee, resize_keyboard=True)
order_types_markup_ru = ReplyKeyboardMarkup(order_types_keyboard_ru, resize_keyboard=True)
order_types_markup_en = ReplyKeyboardMarkup(order_types_keyboard_en, resize_keyboard=True)

confirm_keyboard_ru = [["✅ Подтвердить", "✏ Изменить", "❌ Отменить"]]
confirm_keyboard_en = [["✅ Confirm", "✏ Change", "❌ Cancel"]]
confirm_keyboard_ee = [["✅ Kinnita", "✏ Muuda", "❌ Tühista"]]

confirm_markup_ee = ReplyKeyboardMarkup(confirm_keyboard_ee, resize_keyboard=True)
confirm_markup_ru = ReplyKeyboardMarkup(confirm_keyboard_ru, resize_keyboard=True)
confirm_markup_en = ReplyKeyboardMarkup(confirm_keyboard_en, resize_keyboard=True)

# --- Клавиатуры для Urban Buns (с кнопкой Готово) ---
urban_sub_keyboard_ru = [["1", "2", "3", "4"],["5", "6", "7"], ["Батат", "Картошка фри", "Напитки"], ["✅ Готово"]]
urban_sub_keyboard_en = [["1", "2", "3", "4"],["5", "6", "7"], ["Sweet Potato", "Fries", "Drinks"], ["✅ Done"]]
urban_sub_keyboard_ee = [["1", "2", "3", "4"],["5", "6", "7"], ["Bataat", "Friikartulid", "Joogid"], ["✅ Valmis"]]

urban_sub_markup_ru = ReplyKeyboardMarkup(urban_sub_keyboard_ru, resize_keyboard=True)
urban_sub_markup_en = ReplyKeyboardMarkup(urban_sub_keyboard_en, resize_keyboard=True)
urban_sub_markup_ee = ReplyKeyboardMarkup(urban_sub_keyboard_ee, resize_keyboard=True)

# Клавиатура для напитков
drinks_keyboard_ru = [["1", "2", "3"], ["⬅️ Назад"]]
drinks_keyboard_en = [["1", "2", "3"], ["⬅️ Back"]]
drinks_keyboard_ee = [["1", "2", "3"], ["⬅️ Tagasi"]]

drinks_markup_ru = ReplyKeyboardMarkup(drinks_keyboard_ru, resize_keyboard=True)
drinks_markup_en = ReplyKeyboardMarkup(drinks_keyboard_en, resize_keyboard=True)
drinks_markup_ee = ReplyKeyboardMarkup(drinks_keyboard_ee, resize_keyboard=True)

lang_markup = ReplyKeyboardMarkup(lang_keyboard, resize_keyboard=True)

RECEIPT_LABELS = {
    "Русский": {
        "title": "📝 <b>Ваш чек:</b>",
        "items_header": "Товары:",
        "delivery": "Доставка",
        "total": "Итого к оплате",
        "address": "📍 Адрес",
        "time": "⏰ Время",
        "phone": "📞 Тел",
        "comment": "💬 Комментарий"
    },
    "English": {
        "title": "📝 <b>Your receipt:</b>",
        "items_header": "Items:",
        "delivery": "Delivery",
        "total": "Total to pay",
        "address": "📍 Address",
        "time": "⏰ Time",
        "phone": "📞 Phone",
        "comment": "💬 Comment"
    },
    "Eesti": {
        "title": "📝 <b>Sinu arve:</b>",
        "items_header": "Tooted:",
        "delivery": "Transport",
        "total": "Tasuda kokku",
        "address": "📍 Aadress",
        "time": "⏰ Aeg",
        "phone": "📞 Tel",
        "comment": "💬 Kommentaar"
    }
}

# Цены на позиции Urban Buns
MENU_PRICES_NAL = {
    "Onion King": 10.0,
    "Burning Smash": 10.0,
    "Truhfvel God": 10.0,
    "Gorgonzola Mess": 10.0,
    "Smoky Bastad": 10.0,
    "BinGo Set": 12.0,
    "Bataat": 4.5,
    "Fries": 3.5,
    "Cola": 2.5,
    "Cola Zero": 2.5,
    "Lipton": 2.5
}
MENU_PRICES_BANK = {
    "Onion King": 12.0,
    "Burning Smash": 12.0,
    "Truhfvel God": 12.0,
    "Gorgonzola Mess": 12.0,
    "Smoky Bastad": 12.0,
    "BinGo Set": 12.0,
    "Bataat": 4.5,
    "Fries": 3.5,
    "Cola": 2.5,
    "Cola Zero": 2.5,
    "Lipton": 2.5
}
# Базовые тарифы доставки (минимальная цена)
DELIVERY_TARIFFS = {
    "🍔 Urban Buns": 0.0,

    # 🚲 велосипед
    "🚲 Велодоставка": 4.0,
    "🚲 Bike delivery": 4.0,
    "🚲 Jalgratas": 4.0,

    # 🚗 машина
    "🚗 Машина": 6.0,
    "🚗 Car delivery": 6.0,
    "🚗 Auto": 6.0,

    # 📦 купить и привезти
    "Купить и привезти": 4.0,
    "Buy and deliver": 4.0,
    "Osta ja too": 4.0,

    # 🚚 забрать и отвезти (A → B)
    "Забрать и отвезти": 5.0,
    "Pick up and deliver": 5.0,
    "Võta peale ja vii kohale": 5.0,

    # 📦 другое
    "Другое": 6.0,
    "Other": 6.0,
    "Muu": 6.0
}
# --- Тексты на двух языках ---
TEXTS = {
    "Русский": {
        "urban_menu": (
            "<b>Минимальный заказ — от 12€</b>\n\n"
            "<b>Бургеры: (12€)</b>\n\n"
            "1) ONION KING\n2) BURNING SMASH\n3) TRUHFVEL GOD\n"
            "4) GORGONZOLA MESS\n5) SMOKY BASTAD\n\n"
            "<b>🔥BinGo SPECIAL SET A🔥: (15€)</b>\n"
            "6) Бургер + картошка фри + напиток\n\n"
            "<b>🔥BinGo SPECIAL SET B🔥: (17€)</b>\n"
            "7) Бургер + батат + напиток\n\n"
            "<b>💥Дополнительно💥</b>\n\n"
            "Закуски:\n"
            "8) БАТАТ - 4,5€\n9) КАРТОШКА ФРИ - 3,5€\n\n"
            "Напитки:\n"
            "10) Cola, Cola zero, Lipton (0,33л) - 2,5€"
        ),
        "drink_menu": "🥤 <b>Выберите напиток (0.33л) — 2,5€:</b>\n\n1) Cola\n2) Cola Zero\n3) Lipton",
        "urban_choose": "Выберите позицию из меню Urban Bans:",
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
        "contact_admin": "📩 Напишите админу: @mrjkie",
        "choose_action": "Выберите действие:",
        "order_address_from": "📍 Введите адрес, ОТКУДА забрать:",
        "order_address_to": "📍 Введите адрес, КУДА доставить:"
    },
    "English": {
        "urban_menu": (
            "<b>Minimum order — from 12€</b>\n\n"
            "<b>Burgers: (12€)</b>\n\n"
            "1) ONION KING\n2) BURNING SMASH\n3) TRUHFVEL GOD\n"
            "4) GORGONZOLA MESS\n5) SMOKY BASTAD\n\n"
            "<b>🔥BinGo SPECIAL SET A🔥: (15€)</b>\n"
            "6) Burger + fries + drink\n\n"
            "<b>🔥BinGo SPECIAL SET B🔥: (17€)</b>\n"
            "7) Burger + sweet potato fries + drink\n\n"
            "<b>💥Extras💥</b>\n\n"
            "Snacks:\n"
            "8) SWEET POTATO FRIES – €4.5\n9) FRENCH FRIES – €3.5\n\n"
            "Drinks:\n"
            "10) Cola, Cola Zero, Lipton (0.33 l) – 2.5€"
        ),
        "drink_menu": "🥤 <b>Choose a drink (0.33l) — 2,5€:</b>\n\n1) Cola\n2) Cola Zero\n3) Lipton",
        "urban_choose": "Choose an item from the Urban Bans menu:",
        "choose_lang": "Hello! 👋 Choose language:",
        "main_menu": "🏠 Main menu:",
        "create_order": "📦 Create order",
        "my_orders": "📋 My orders",
        "tariffs": "💰 Tariffs",
        "rules": "📜 Rules",
        "contact_operator": "👨‍💻 Contact operator",
        "order_type": "📦 Select order type:",
        "order_description": "📝 Describe your order (what to buy/deliver):",
        "order_address": "📍 Enter delivery address:",
        "order_time": "⏰ Delivery time:",
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
        "contact_admin": "📩 Send a message to the admin: @mrjkie",
        "choose_action": "Choose action:",
        "order_address_from": "📍 Enter the PICKUP address:",
        "order_address_to": "📍 Enter the DELIVERY address:"
    },
    "Eesti": {
        "urban_menu": (
            "<b>Minimaalne tellimus — alates 12€</b>\n\n"
            "<b>Burgerid: (12€)</b>\n\n"
            "1) ONION KING\n2) BURNING SMASH\n3) TRUHFVEL GOD\n"
            "4) GORGONZOLA MESS\n5) SMOKY BASTAD\n\n"
            "<b>🔥BinGo SPECIAL SET A🔥: (15€)</b>\n"
            "6) Burger + friikartulid + jook\n\n"
            "<b>🔥BinGo SPECIAL SET B🔥: (17€)</b>\n"
            "7) Burger + bataat + jook\n\n"
            "<b>💥Lisaks💥</b>\n\n"
            "Suupisted:\n"
            "8) BATAAT – 4,5€\n9) FRIIKARTULID – 3,5€\n\n"
            "Joogid:\n"
            "10) Cola, Cola zero, Lipton (0,33 l) – 2.5€"
        ),
        "drink_menu": "🥤 <b>Vali jook (0.33l) — 2,5€:</b>\n\n1) Cola\n2) Cola Zero\n3) Lipton",
        "urban_choose": "Valige Urban Bans menüüst:",
        "choose_lang": "Tere! 👋 Vali keel:",
        "main_menu": "🏠 Peamenüü:",
        "create_order": "📦 Loo tellimus",
        "my_orders": "📋 Minu tellimused",
        "tariffs": "💰 Hinnad",
        "rules": "📜 Reeglid",
        "contact_operator": "👨‍💻 Võta ühendust operaatoriga",
        "order_type": "📦 Vali tellimuse tüüp:",
        "order_description": "📝 Kirjelda oma tellimust:",
        "order_address": "📍 Sisesta aadress:",
        "order_time": "⏰ Tarneaeg:",
        "contact_name": "👤 Sisesta oma nimi:",
        "contact_phone": "📞 Sisesta oma telefon:",
        "comment": "💬 Kommentaar (valikuline):",
        "confirm": "✅ Kinnita",
        "change": "✏ Muuda",
        "cancel": "❌ Tühista",
        "order_accepted": "✅ Tellimus vastu võetud!\n📦 Number: #{id}\n📊 Staatus: Uus",
        "invalid_option": "Palun vali menüüst.",
        "my_orders_empty": "Sul pole veel tellimusi.",
        "tariffs_text": "💰 Hinnad:\n🍔 Urban Buns — tasuta\n🚲 Jalgratas — alates 4€\n🚗 Auto — alates 6€\n⚙️ Keerulised tellimused — kokkuleppel",
        "rules_text": "📜 Reeglid:\n- ✅ Ainult legaalsed kaubad\n- ❌ Narkootikumid ja relvad keelatud\n- 🔍 Kuller võib tellimust täpsustada\n- 🚫 Teenus võib keelduda",
        "contact_admin": "📩 Kirjuta adminile: @mrjkie",
        "choose_action": "Vali tegevus:",
        "order_address_from": "📍 Sisesta aadress, KUST peale võtta:",
        "order_address_to": "📍 Sisesta aadress, KUHU viia:"
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
    created_at TEXT,
    total_price FLOAT
)
""")
conn.commit()

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
        if text not in ["Русский", "English", "Eesti"]:
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
        elif text == "English":
            menu_markup = main_menu_markup_en
            msg = "You chose language: English"
        else:
            menu_markup = main_menu_markup_ee
            msg = "Sa valisid keele: Eesti"

        await update.message.reply_text(msg, reply_markup=menu_markup)
        return
    
    # --- Главное меню ---
    if stage == "main_menu":
    # --- правильный выбор клавиатуры ---
        if lang == "Русский":
            menu_markup = main_menu_markup_ru
        elif lang == "English":
            menu_markup = main_menu_markup_en
        else:
            menu_markup = main_menu_markup_ee

        if text == TEXTS[lang]["create_order"]:
            context.user_data["stage"] = "order_type"

            # --- клавиатура типов заказа ---
            if lang == "Русский":
                markup = order_types_markup_ru
            elif lang == "English":
                markup = order_types_markup_en
            else:
                markup = order_types_markup_ee

            await update.message.reply_text(TEXTS[lang]["order_type"], reply_markup=markup)

        elif text == TEXTS[lang]["my_orders"]:
            user_id = update.message.from_user.id
            cursor.execute(
                "SELECT id, type, status, created_at FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 5",
                (user_id,)
            )
            orders = cursor.fetchall()

            if orders:
                # 👉 можно позже тоже перевести, но пока оставим так
                msg = "Ваши заказы:\n" + "\n".join(
                    [f"#{o[0]} | {o[1]} | {o[2]} | {o[3]}" for o in orders]
                )
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

        # --- 1. Выбор типа заказа ---
    if stage == "order_type":
        # (Тут твоя логика определения markup и valid_options...)
        if lang == "Русский":
            markup = order_types_markup_ru
            valid_options = [item for row in order_types_keyboard_ru for item in row]
        elif lang == "English":
            markup = order_types_markup_en
            valid_options = [item for row in order_types_keyboard_en for item in row]
        else:
            markup = order_types_markup_ee
            valid_options = [item for row in order_types_keyboard_ee for item in row]

        if text not in valid_options:
            await update.message.reply_text(TEXTS[lang]["order_type"], reply_markup=markup)
            return

        context.user_data["order_type"] = text
        context.user_data["is_pickup"] = False

        pickup_keywords = ["Забрать и отвезти", "Pick up and deliver", "Võta peale ja vii kohale"]
        
        if any(keyword in text for keyword in pickup_keywords):
            context.user_data["is_pickup"] = True
            context.user_data["stage"] = "order_address_from"
            await update.message.reply_text(TEXTS[lang]["order_address_from"], reply_markup=ReplyKeyboardRemove())
        
            return
        # ПРОВЕРКА: Если выбрали Urban Buns
        elif "Urban Buns" in text:
            context.user_data["stage"] = "urban_sub_menu"
            context.user_data["cart"] = [] # Создаем пустую корзину
            
            sub_markup = urban_sub_markup_ru if lang == "Русский" else urban_sub_markup_en if lang == "English" else urban_sub_markup_ee
            
            await update.message.reply_text(TEXTS[lang]["urban_menu"], parse_mode="HTML")
            
            # Текст подсказки на разных языках
            instruction = {
                "Русский": "Выберите позиции. Когда закончите — нажмите «✅ Готово»",
                "English": "Choose items. When finished, press «✅ Done»",
                "Eesti": "Valige tooted. Kui olete lõpetanud, vajutage «✅ Valmis»"
            }
            await update.message.reply_text(instruction[lang], reply_markup=sub_markup)
            return

        # Для всех остальных типов заказов (не Urban Buns)
        context.user_data["stage"] = "order_description"
        await update.message.reply_text(TEXTS[lang]["order_description"], reply_markup=ReplyKeyboardRemove())
        return

    # --- 2. НОВЫЙ ЭТАП: Обработка корзины Urban Buns (МНОЖЕСТВЕННЫЙ ВЫБОР) ---
    # --- ЭТАП: Основное меню Urban Buns (Бургеры и Закуски) ---
    elif stage == "urban_sub_menu":
        done_triggers = ["✅ Готово", "✅ Done", "✅ Valmis"]
        drinks_triggers = ["Напитки", "Drinks", "Joogid"]

        burger_map = {
            # Бургеры по номеру
            "1": "Onion King",
            "2": "Burning Smash",
            "3": "Truhfvel God",
            "4": "Gorgonzola Mess",
            "5": "Smoky Bastad",
            "6": "BinGo SPECIAL SET A",
            "7": "BinGo SPECIAL SET B",

            # Гарниры
            "Батат": "Bataat",
            "Sweet Potato": "Bataat",
            "Bataat": "Bataat",
            "Картошка фри": "Fries",
            "Fries": "Fries",
            "Friikartulid": "Fries",

            # Напитки
            "Cola": "Cola",
            "Cola Zero": "Cola Zero",
            "Lipton": "Lipton"
        }
        # --- Завершение заказа ---
        if text in done_triggers:
            if not context.user_data.get("cart"):
                await update.message.reply_text("Вы ничего не выбрали!")
                return

            final_list = ", ".join(context.user_data["cart"])
            context.user_data["description"] = f"Urban Buns: {final_list}"
            context.user_data["stage"] = "order_address"
            await update.message.reply_text(TEXTS[lang]["order_address"], reply_markup=ReplyKeyboardRemove())
            return

        # --- Переход к напиткам ---
        if text in drinks_triggers:
            context.user_data["stage"] = "urban_drinks_menu"
            markup = drinks_markup_ru if lang=="Русский" else drinks_markup_en if lang=="English" else drinks_markup_ee
            await update.message.reply_text(TEXTS[lang]["drink_menu"], reply_markup=markup, parse_mode="HTML")
            return

        item_name = burger_map.get(text, text)

        # --- Обработка сетов ---
        if item_name in ["BinGo SPECIAL SET A", "BinGo SPECIAL SET B"]:
            context.user_data["current_set"] = {"set": item_name, "burger": None, "drink": None}
            context.user_data["stage"] = "choose_set_burger"

            # Выбор бургера для сета
            burger_options = ["Onion King", "Burning Smash", "Truhfvel God", "Gorgonzola Mess", "Smoky Bastad"]
            markup = ReplyKeyboardMarkup([[b] for b in burger_options], one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text(f"Выберите бургер для {item_name}:", reply_markup=markup)
            return

        # --- Обычные товары ---
        if item_name in ["Onion King", "Burning Smash", "Truhfvel God", "Gorgonzola Mess", "Smoky Bastad",
                         "Bataat", "Fries", "Cola", "Cola Zero", "Lipton"]:
            if "cart" not in context.user_data:
                context.user_data["cart"] = []
            context.user_data["cart"].append(item_name)

            item_count = context.user_data["cart"].count(item_name)
            current_cart_text = "\n".join([f"• {i}" for i in context.user_data["cart"]])

            added_msg = {
                "Русский": f"✅ Добавлено: {item_name} (в корзине: {item_count} шт.)\n\n<b>Ваш заказ:</b>\n{current_cart_text}",
                "English": f"✅ Added: {item_name} (in cart: {item_count} pcs)\n\n<b>Your order:</b>\n{current_cart_text}",
                "Eesti": f"✅ Lisatud: {item_name} (ostukorvis: {item_count} tk)\n\n<b>Sinu tellimus:</b>\n{current_cart_text}"
            }

            await update.message.reply_text(added_msg[lang], parse_mode="HTML")
            return

    # --- Выбор бургера для сета ---
    elif stage == "choose_set_burger":
        context.user_data["current_set"]["burger"] = text
        context.user_data["stage"] = "choose_set_drink"

        drink_options = ["Cola", "Cola Zero", "Lipton"]
        markup = ReplyKeyboardMarkup([[d] for d in drink_options], one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text("Выберите напиток для сета:", reply_markup=markup)

    # --- Выбор напитка для сета ---
    elif stage == "choose_set_drink":
        context.user_data["current_set"]["drink"] = text
        current_set = context.user_data.pop("current_set")

        side = "Fries" if "A" in current_set["set"] else "Bataat"
        cart_item = f"{current_set['set']}: {current_set['burger']} + {side} + {current_set['drink']}"

        if "cart" not in context.user_data:
            context.user_data["cart"] = []
        context.user_data["cart"].append(cart_item)

        current_cart_text = "\n".join([f"• {i}" for i in context.user_data["cart"]])
        await update.message.reply_text(
            f"✅ {cart_item} добавлен в корзину.\n\n<b>Ваш заказ:</b>\n{current_cart_text}",
            reply_markup=urban_sub_markup_ru if lang=="Русский" else urban_sub_markup_en if lang=="English" else urban_sub_markup_ee,
            parse_mode="HTML"
        )

        context.user_data["stage"] = "urban_sub_menu"

        # Если нажимают на кнопки товаров
        if "cart" not in context.user_data:
            context.user_data["cart"] = []
        
        context.user_data["cart"].append(text)
        
        # Считаем количество именно этого товара
        item_count = context.user_data["cart"].count(text)
        
        # Список всей корзины для наглядности
        current_cart_text = "\n".join([f"• {item}" for item in context.user_data["cart"]])
        
        added_msg = {
            "Русский": f"✅ Добавлено: {text} (в корзине: {item_count} шт.)\n\n<b>Ваш заказ:</b>\n{current_cart_text}",
            "English": f"✅ Added: {text} (in cart: {item_count} pcs)\n\n<b>Your order:</b>\n{current_cart_text}",
            "Eesti": f"✅ Lisatud: {text} (ostukorvis: {item_count} tk)\n\n<b>Sinu tellimus:</b>\n{current_cart_text}"
        }

        await update.message.reply_text(added_msg[lang], parse_mode="HTML")
        return
        if text in drinks_triggers:
            context.user_data["stage"] = "urban_drinks_menu"
            markup = drinks_markup_ru if lang == "Русский" else drinks_markup_en if lang == "English" else drinks_markup_ee
            await update.message.reply_text(TEXTS[lang]["drink_menu"], reply_markup=markup, parse_mode="HTML")
            return

        # --- проверка корректности ввода ---
        if text not in valid_options:
            await update.message.reply_text(TEXTS[lang]["order_type"], reply_markup=markup)
            return

        context.user_data["order_type"] = text
        context.user_data["stage"] = "order_description"

        await update.message.reply_text(
            TEXTS[lang]["order_description"],
            reply_markup=ReplyKeyboardRemove()
        )
    # --- ЭТАП: Адрес А (Откуда) ---
    elif stage == "order_address_from":
        context.user_data["address_from"] = text
        context.user_data["stage"] = "order_address_to"
        
        msg_to = {
            "Русский": "📍 Теперь введите адрес, КУДА доставить:",
            "English": "📍 Now enter the DELIVERY address:",
            "Eesti": "📍 Nüüd sisesta aadress, KUHU viia:"
        }
        await update.message.reply_text(msg_to[lang])
        return  # <--- КРИТИЧЕСКИ ВАЖНО! Без этого он прыгнет в следующий elif

    # --- ЭТАП: Адрес Б (Куда) ---
    elif stage == "order_address_to":
        context.user_data["address_to"] = text
        # Сохраняем общую строку адреса для чека
        context.user_data["address"] = f"A: {context.user_data['address_from']} -> B: {context.user_data['address_to']}"
        
        # Переходим к описанию заказа
        context.user_data["stage"] = "order_description"
        await update.message.reply_text(TEXTS[lang]["order_description"], reply_markup=ReplyKeyboardRemove())
        return
    
    # --- Описание заказа ---
    elif stage == "order_description":
        context.user_data["description"] = text

        # 🔥 ЕСЛИ это A → B — пропускаем повторный ввод адреса
        if context.user_data.get("is_pickup"):
            context.user_data["stage"] = "order_time"
            await update.message.reply_text(TEXTS[lang]["order_time"])
        else:
            context.user_data["stage"] = "order_address"
            await update.message.reply_text(TEXTS[lang]["order_address"], reply_markup=ReplyKeyboardRemove())

        return

    # --- Обычный адрес (для Urban Buns и других типов) ---
    elif stage == "order_address":
        context.user_data["address"] = text
        context.user_data["stage"] = "order_time"
        await update.message.reply_text(TEXTS[lang]["order_time"], reply_markup=ReplyKeyboardRemove())
        return

    # --- Время ---
    elif stage == "order_time":
        # варианты "как можно скорее" на разных языках
        asap_options = [
            "как можно скорее",
            "as soon as possible",
            "nii kiiresti kui võimalik"
        ]

        if text.lower() in asap_options:
            context.user_data["time"] = text
        else:
            context.user_data["time"] = text

        context.user_data["stage"] = "order_contact_name"

        await update.message.reply_text(
            TEXTS[lang]["contact_name"],
            reply_markup=ReplyKeyboardRemove()
        )
        return

    # --- Имя ---
    elif stage == "order_contact_name":
        context.user_data["name"] = text
        context.user_data["stage"] = "order_contact_phone"
        await update.message.reply_text(TEXTS[lang]["contact_phone"], reply_markup=ReplyKeyboardRemove())
        return

    # --- Телефон ---
    elif stage == "order_contact_phone":
        context.user_data["phone"] = text
        context.user_data["stage"] = "order_comment"
        await update.message.reply_text(TEXTS[lang]["comment"], reply_markup=ReplyKeyboardRemove())
        return

    elif stage == "order_comment":
        context.user_data["comment"] = text
        context.user_data["stage"] = "order_confirm"
        
        lang = context.user_data.get("language", "Русский")
        labels = RECEIPT_LABELS[lang]

        # 1. Сбор данных
        cart = context.user_data.get("cart", [])
        order_type = context.user_data.get("order_type", "")

        # 2. Расчет доставки
        delivery_sum = 0.0
        for key, price in DELIVERY_TARIFFS.items():
            if key in order_type:
                delivery_sum = price
                break
        
        # 3. Расчет суммы товаров для ОБОИХ вариантов
        items_sum_nal = sum(MENU_PRICES_NAL.get(item, 0) for item in cart)
        items_sum_bank = sum(MENU_PRICES_BANK.get(item, 0) for item in cart)

        total_nal = items_sum_nal + delivery_sum
        total_bank = items_sum_bank + delivery_sum

        # Сохраняем строку с двумя ценами для базы данных
        context.user_data["total_price"] = f"{total_nal}€ (Нал) / {total_bank}€ (Карта)"

        # 4. Собираем список товаров для чека (просто названия)
        cart_details = ""
        if cart:
            cart_list = "\n".join([f"• {i}" for i in cart])
            cart_details = f"\n{labels['items_header']}\n{cart_list}\n"

        # Текстовка для цен на разных языках
        price_titles = {
            "Русский": f"💵 Наличными: <b>{total_nal}€</b>\n💳 Картой: <b>{total_bank}€</b>",
            "English": f"💵 Cash: <b>{total_nal}€</b>\n💳 Card: <b>{total_bank}€</b>",
            "Eesti": f"💵 Sularahas: <b>{total_nal}€</b>\n💳 Kaardiga: <b>{total_bank}€</b>"
        }

        # 5. Формируем итоговое сообщение
        order_summary = (
            f"{labels['title']}\n"
            f"{cart_details}"
            f"-------------------------------\n"
            f"🚚 {labels['delivery']}: {delivery_sum}€\n\n"
            f"{price_titles[lang]}\n"
            f"-------------------------------\n"
            f"{labels['address']}: {context.user_data['address']}\n"
            f"{labels['time']}: {context.user_data['time']}\n"
            f"{labels['phone']}: {context.user_data['phone']}\n"
            f"{labels['comment']}: {context.user_data['comment']}"
        )

        markup = confirm_markup_ru if lang == "Русский" else confirm_markup_en if lang == "English" else confirm_markup_ee
        await update.message.reply_text(order_summary, reply_markup=markup, parse_mode="HTML")
        return

        # --- мультиязычный summary ---
        if lang == "Русский":
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
            markup = confirm_markup_ru

        elif lang == "English":
            order_summary = (
                f"📦 Your order:\n"
                f"📋 Order type: {context.user_data['order_type']}\n"
                f"📝 Description: {context.user_data['description']}\n"
                f"📍 Address: {context.user_data['address']}\n"
                f"⏰ Time: {context.user_data['time']}\n"
                f"👤 Name: {context.user_data['name']}\n"
                f"📞 Phone: {context.user_data['phone']}\n"
                f"💬 Comment: {context.user_data['comment']}"
            )
            markup = confirm_markup_en

        else:  # Eesti
            order_summary = (
                f"📦 Sinu tellimus:\n"
                f"📋 Tüüp: {context.user_data['order_type']}\n"
                f"📝 Kirjeldus: {context.user_data['description']}\n"
                f"📍 Aadress: {context.user_data['address']}\n"
                f"⏰ Aeg: {context.user_data['time']}\n"
                f"👤 Nimi: {context.user_data['name']}\n"
                f"📞 Telefon: {context.user_data['phone']}\n"
                f"💬 Kommentaar: {context.user_data['comment']}"
            )
            markup = confirm_markup_ee

        context.user_data["stage"] = "order_confirm"

        await update.message.reply_text(order_summary, reply_markup=markup)

    # --- Подтверждение заказа ---
    if stage == "order_confirm":
        menu_markup = main_menu_markup_ru if lang == "Русский" else main_menu_markup_en if lang == "English" else main_menu_markup_ee
        if text == TEXTS[lang]["confirm"]:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Сохраняем заказ в базе
            cursor.execute("""
                INSERT INTO orders (user_id, username, language, type, description, address, time, name, phone, comment, status, created_at, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                now,
                context.user_data.get("total_price", 0)
            ))
            conn.commit()
            order_id = cursor.lastrowid
        

            # --- Уведомление заказчику ---
            menu_markup = main_menu_markup_ru if lang == "Русский" else main_menu_markup_en if lang == "English" else main_menu_markup_ee
            await update.message.reply_text(TEXTS[lang]["order_accepted"].format(id=order_id), reply_markup=menu_markup)

            context.user_data["stage"] = "main_menu"
            # --- Уведомление админу ---
            admin_message = (
                f"📦 Новый заказ #{order_id}\n\n"
                f"👤 Пользователь: {context.user_data['username']} ({context.user_data['user_id']})\n"
                f"📋 Тип: {context.user_data['order_type']}\n"
                f"📝 Описание: {context.user_data['description']}\n"
                f"📍 Адрес: {context.user_data['address']}\n"
                f"⏰ Время: {context.user_data['time']}\n"
                f"📞 Телефон: {context.user_data.get('phone','')}\n"
                f"💬 Комментарий: {context.user_data.get('comment','')}\n"
                f"💰 Цена: {context.user_data.get('total_price','')}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
            

        elif text == TEXTS[lang]["change"]:
            context.user_data["stage"] = "order_description"
            await update.message.reply_text(TEXTS[lang]["order_description"], reply_markup=None)
        # --- Отмена заказа ---
        elif text == TEXTS[lang]["cancel"] or text == "❌ Tühista":
            # Очистка данных заказа
            keys_to_clear = ["order_type", "description", "address", "time", "name", "phone", "comment"]
            for key in keys_to_clear:
                context.user_data.pop(key, None)
            context.user_data["stage"] = "main_menu"

            # Главное меню в зависимости от языка
            if lang == "Русский":
                menu_markup = main_menu_markup_ru
                cancel_msg = "❌ Заказ отменён."
            elif lang == "English":
                menu_markup = main_menu_markup_en
                cancel_msg = "❌ Order cancelled."
            elif lang == "Eesti":
                menu_markup = main_menu_markup_ee
                cancel_msg = "❌ Tellimus tühistatud."
            else:
                # На всякий случай, если язык неизвестен
                menu_markup = main_menu_markup_ru
                cancel_msg = "❌ Заказ отменён."

            await update.message.reply_text(cancel_msg, reply_markup=menu_markup)
        else:
            markup = confirm_markup_ru if lang == "Русский" else confirm_markup_en if lang == "English" else confirm_markup_ee
            await update.message.reply_text(TEXTS[lang]["choose_action"], reply_markup=markup)
        return

# --- Запуск бота ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()
