# UCstore.py — Full version (async, python-telegram-bot v20+)
# NOTE: Replace TOKEN with your bot token before running.

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import datetime
import json
import os
import random
import string

# -------------------- Config --------------------
TOKEN = "8394642029:AAH50ltfmxyRRBnPm3QTa3LAtx8MeDSqBU0"  # <-- change this
ADMIN_IDS = [8436218638]
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"

ITEMS = {
    1: {"name": "💎100+5", "price": 10},
    2: {"name": "💎310+16", "price": 28},
    3: {"name": "💎520+26", "price": 48},
    4: {"name": "💎1060+53", "price": 105},
    5: {"name": "💎2180+218", "price": 210},
    6: {"name": "💎5600+560", "price": 480},
}

VOUCHERS = {
    101: {"name": "Ваучер на неделю 450💎", "price": 17},
    102: {"name": "Ваучер на месяц 2600💎", "price": 95},
    103: {"name": "Ваучер лайт 90💎", "price": 7},
}

ADMIN_INSTAGRAM = "https://www.instagram.com/garant_alestr?igsh=cTE4bnA3NW5ycHFs"
ADMIN_TELEGRAM = "https://t.me/dilshodsss33"

ADMIN_INFO = (
    """UCstore — ин боти расмии фурӯши UC барои PUBG Mobile ва дигар хидматҳои рақамии бозӣ мебошад. Мо барои бозингарони тоҷик платформаи боэътимод, босифат ва осонро фароҳам овардаем, то харид кардан осон, бехатар ва зуд сурат гирад. ⚡️

🔹 Афзалиятҳои UCstore:

🎁 UC-и ройгон 

🫴Мо ба шумо ҳаруз аз 1 то 5 uc-и ройгон медиҳем ва инчунин бо даъвати ҳар як дуст шумо 2 uc ба даст меоред.

• 🛍 Каталоги пурра бо нархҳои дастрас
• 💳 Усулҳои гуногуни пардохт (аз ҷумла роҳи нави корти милли ва  VISA)
• ⚙️ Системаи автоматии фармоиш ва тасдиқ
• 💬 Пуштибонии зуд аз ҷониби админ
• ❤️ Имкони илова ба “дилхоҳҳо” ва сабади шахсӣ
• 🔔 Огоҳии фаврӣ дар бораи ҳолати фармоиш

📦 Чӣ тавр кор мекунад:
1️⃣ Ба бот ворид шавед
2️⃣ Маҳсулоти дилхоҳатонро интихоб кунед
3️⃣ Фармоиш диҳед ва пардохтро анҷом диҳед
4️⃣ Мунтазир шавед — UC ба ҳисоби шумо фиристода мешавад 🎁

🤝 Бартарии мо — шаффофият, суръат ва эътимод.
Ҳар як фармоиш боэҳтиёт санҷида мешавад, то мизоҷон таҷрибаи беҳтарин гиранд.

Бо UCstore шумо ҳамеша бехатар, зуд ва бо эътимод харид мекунед 💪

Инчунин дар бораи тамоми мушкилот шумо ҳамеша метавонед ба админ тамос гиред @MARZBON_TJ"""
)

VISA_NUMBER = "4439200020432471"
SBER_NUMBER = "2202208496090011"
FREE_UC_CHANNEL = "@marzbon_media"

# -------------------- Persistence --------------------

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_all():
    save_json(USERS_FILE, users_data)
    save_json(ORDERS_FILE, orders)


users_data = load_json(USERS_FILE, {})  # key: user_id (str) -> info
orders = load_json(ORDERS_FILE, [])  # list of orders

# Runtime structures (not persisted)
user_carts = {}
user_wishlist = {}
broadcast_mode = {}

# -------------------- Helpers --------------------

def generate_user_code(length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def get_item_type(item_id: int) -> str:
    if item_id in ITEMS:
        return "Алмаз"
    if item_id in VOUCHERS:
        return "Ваучер"
    return "Номаълум"


def _create_order_record(user_id: str, total: int, extra=None) -> dict:
    order_id = random.randint(10000, 99999)
    order = {
        "id": order_id,
        "user_id": user_id,
        "user_name": users_data.get(user_id, {}).get("name", ""),
        "username": users_data.get(user_id, {}).get("username", ""),
        "phone": users_data.get(user_id, {}).get("phone", ""),
        "total": total,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "extra": extra or {},
    }
    orders.append(order)
    save_all()
    return order
   
# -------------------- New function: math challenge after contact --------------------
async def _start_math_challenge_for_new_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str):
    """
    Start a simple math challenge (addition or subtraction randomly) for newly registered user.
    Stores expected answer and attempts in context.user_data and asks the user to reply with the answer.
    After success or exhausting attempts, the main menu is shown.
    """
    # Choose operation randomly: addition or subtraction (user selected option 3 earlier)
    op = random.choice(["+", "-"])
    if op == "+":
        a = random.randint(1, 50)
        b = random.randint(1, 50)
        answer = a + b
        expr = f"{a} + {b}"
    else:
        # For subtraction ensure non-negative result
        a = random.randint(1, 50)
        b = random.randint(1, a)  # b <= a
        answer = a - b
        expr = f"{a} - {b}"

    # Save challenge in user-specific context
    context.user_data["awaiting_math_answer"] = True
    context.user_data["math_answer"] = answer
    context.user_data["math_attempts"] = 0
    context.user_data["math_max_attempts"] = 3
    # Store user_id to call show_main_menu later
    context.user_data["math_for_user_id"] = user_id

    # Send the challenge
    if update.message:
        chat = update.message.chat
    elif update.callback_query:
        chat = update.callback_query.message.chat
    else:
        # fallback; try bot to send to user_id
        try:
            await context.bot.send_message(int(user_id), f"🔐 Барои идома додан як санҷиши кӯчак: {expr} = ?\n(Ҷавобро танҳо бо рақам нависед)")
        except Exception:
            pass
        return

    await chat.send_message(
        f"🔐 Барои идома додан як санҷиши кӯчак: {expr} = ?\n(Ҷавобро танҳо бо рақам нависед)\n📌 Шумо 3 кӯшиш доред."
    )


async def _check_math_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check the user's reply to the math challenge. If correct -> show main menu.
    If incorrect and attempts remain -> ask to try again.
    If attempts exhausted -> notify and show main menu.
    """
    if not context.user_data.get("awaiting_math_answer"):
        return

    text = (update.message.text or "").strip()
    user_id = str(update.message.from_user.id)
    expected = context.user_data.get("math_answer")

    # Basic validation: must be an integer (allow negative though unlikely)
    try:
        given = int(text)
    except Exception:
        context.user_data["math_attempts"] += 1
        attempts_left = context.user_data["math_max_attempts"] - context.user_data["math_attempts"]
        if attempts_left > 0:
            await update.message.reply_text(f"⚠️ Ҷавоб бояд рақам бошад. Ҳоло {attempts_left} кӯшиш мондааст. Лутфан бо рақам ҷавоб диҳед.")
            return
        else:
            # attempts exhausted
            context.user_data["awaiting_math_answer"] = False
            await update.message.reply_text("❌ Шумо кӯшишҳоро тамом кардед. Ҳангоми ягон проблема бо админ муошират кунед.")
            # show main menu anyway
            try:
                uid = context.user_data.pop("math_for_user_id", user_id)
                await show_main_menu(update.message.chat, uid)
            except Exception:
                pass
            # cleanup
            for k in ["math_answer", "math_attempts", "math_max_attempts", "math_for_user_id"]:
                context.user_data.pop(k, None)
            return

    # Compare answers
    if given == expected:
        context.user_data["awaiting_math_answer"] = False
        await update.message.reply_text("✅ Санҷиш супорида шуд! Шумо бо муваффақият тасдиқ шудед.")
        # cleanup and show main menu
        try:
            uid = context.user_data.pop("math_for_user_id", user_id)
            # ensure other math keys removed
            for k in ["math_answer", "math_attempts", "math_max_attempts"]:
                context.user_data.pop(k, None)
            await show_main_menu(update.message.chat, uid)
        except Exception:
            pass
        return
    else:
        context.user_data["math_attempts"] += 1
        attempts_left = context.user_data["math_max_attempts"] - context.user_data["math_attempts"]
        if attempts_left > 0:
            await update.message.reply_text(f"❌ Ҷавоб нодуруст аст. Қаблан {attempts_left} кӯшиш мондааст. Дубора кӯшиш кунед.")
            return
        else:
            # attempts exhausted
            context.user_data["awaiting_math_answer"] = False
            await update.message.reply_text("❌ Шумо кӯшишҳоро тамом кардед. Агар лозим бошад, бо админ тамос гиред.")
            try:
                uid = context.user_data.pop("math_for_user_id", user_id)
                await show_main_menu(update.message.chat, uid)
            except Exception:
                pass
            for k in ["math_answer", "math_attempts", "math_max_attempts", "math_for_user_id"]:
                context.user_data.pop(k, None)
            return
# -------------------- End of new math functions --------------------


# -------------------- Handlers --------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Entry point. Ask for phone contact if user not registered.
    if not update.message:
        return

    user = update.message.from_user
    user_id = str(user.id)

    # If already registered, show menu
    if user_id in users_data:
        await update.message.reply_text(f"👋 Салом, {user.first_name}!")
        await show_main_menu(update.message.chat, user_id)
        return

    # Ask for contact
    contact_button = KeyboardButton("📱 Ворид шудан бо рақам", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "🔐 Барои истифодаи бот рақами телефони худро фиристед:", reply_markup=reply_markup
    )

async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save contact and create user record
    contact = update.message.contact
    if not contact:
        await update.message.reply_text("⚠️ Лутфан контакт фиристед.")
        return

    user = update.message.from_user
    user_id = str(user.id)

    user_code = generate_user_code(6)
    users_data[user_id] = {
        "id": user.id,
        "name": user.first_name or "",
        "username": user.username or "",
        "phone": contact.phone_number,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "free_uc": 0,
        "last_claim": None,
        "last_daily_uc": None,
        "code": user_code,
    }
    save_all()

    # Handle inviter stored in user_data (if /start payload was used)
    inviter = context.user_data.get("invited_by")
    if inviter and inviter != user_id and str(inviter) in users_data:
        inv = str(inviter)
        users_data[inv]["free_uc"] = users_data[inv].get("free_uc", 0) + 2
        save_all()
        try:
            await context.bot.send_message(
                int(inv),
                f"🎉 Шумо 2 UC барои даъват кардани корбари нав гирифтед!\n"
                f"👤 @{user.username or user.first_name}"
            )
        except Exception:
            pass

    # Notify admins
    for admin in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin,
                (
                    "👤 Корбари нав сабт шуд!\n\n"
                    f"🧑 Ном: {user.first_name}\n"
                    f"📱 Рақам: {contact.phone_number}\n"
                    f"🔗 @{user.username or '—'}\n"
                    f"🔑 Код: {user_code}"
                ),
            )
        except Exception:
            pass

    await update.message.reply_text(
        f"✅ Шумо бо муваффақият ворид шудед!!\n"
        f"🔑 Код шумо: {user_code}",
        reply_markup=ReplyKeyboardRemove()
    )

    # NEW: Start math challenge BEFORE showing main menu
    # store user id as string
    await _start_math_challenge_for_new_user(update, context, user_id)
    # note: show_main_menu will be called after successful math challenge (in _check_math_answer)

async def show_main_menu(chat, user_id: str):
    buttons = [
        ["🛍 Мағоза ", "❤️ Дилхоҳҳо"],
        ["🛒 Сабад", "💬 Профили админ"],
        ["ℹ Маълумот", ],
    ]
    if int(user_id) in ADMIN_IDS:
        buttons.append(["👑 Панели админ"])

    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)
    await chat.send_message("Менюи асосӣ:", reply_markup=reply_markup)


# -------------------- Catalog handlers --------------------

# Менюи асосии каталог (UC / Voucher)
async def catalog_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = update.message or (update.callback_query and update.callback_query.message)
    if not target:
        return

    buttons = [
        [InlineKeyboardButton("💎Алмаз харидан", callback_data="catalog_uc")],
        [InlineKeyboardButton("🎫 Ваучер харидан", callback_data="catalog_voucher")],
        [InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")],
    ]

    await target.reply_text(
        "🛍 мағоза:\nЛутфан интихоб кунед:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# -------------------- almaz catalog --------------------

async def catalog_uc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = []
    row = []
    for i, item in ITEMS.items():
        row.append(
            InlineKeyboardButton(
                f"{item['name']} — {item['price']} TJS",
                callback_data=f"select_{i}",
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")])

    await query.message.edit_text(
        "Хариди Алмаз:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# -------------------- Voucher catalog --------------------

async def catalog_voucher_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    buttons = []
    for i, item in VOUCHERS.items():
        buttons.append([
            InlineKeyboardButton(
                f"{item['name']} — {item['price']} TJS",
                callback_data=f"select_voucher_{i}",
            )
        ])

    buttons.append([InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")])

    await query.message.edit_text(
        "🎫 Ваучер харидан:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# -------------------- Almaz product page --------------------

async def select_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        await query.message.reply_text("⚠️ Хато дар интихоби маҳсулот.")
        return

    item = ITEMS.get(item_id)
    if not item:
        await query.message.reply_text("Маҳсулот ёфт нашуд.")
        return

    buttons = [
        [
            InlineKeyboardButton("🛒 Илова ба сабад", callback_data=f"addcart_{item_id}"),
            InlineKeyboardButton("❤️ Ба дилхоҳҳо", callback_data=f"addwish_{item_id}"),
        ],
        [InlineKeyboardButton("⬅️ Бозгашт", callback_data="catalog_uc")],
    ]

    await query.message.reply_text(
        f"🛍 {item['name']} — {item['price']} TJS",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


# -------------------- Voucher product page --------------------

async def select_voucher_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        voucher_id = int(query.data.split("_")[2])
    except Exception:
        await query.message.reply_text("⚠️ Хато дар интихоби ваучер.")
        return

    item = VOUCHERS.get(voucher_id)
    if not item:
        await query.message.reply_text("Ваучер ёфт нашуд.")
        return

    buttons = [
        [
            InlineKeyboardButton("🛒 Илова ба сабад", callback_data=f"addcart_{voucher_id}"),
            InlineKeyboardButton("❤️ Ба дилхоҳҳо", callback_data=f"addwish_{voucher_id}"),
        ],
        [InlineKeyboardButton("⬅️ Бозгашт", callback_data="catalog_voucher")],
    ]

    await query.message.reply_text(
        f"🎫 {item['name']} — {item['price']} TJS",
        reply_markup=InlineKeyboardMarkup(buttons),
    )

async def addcart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return

    # almaz ё Ваучер
    if item_id not in ITEMS and item_id not in VOUCHERS:
        await query.message.reply_text("⚠️ Маҳсулот ёфт нашуд.")
        return

    user_carts.setdefault(user_id, {})
    user_carts[user_id][item_id] = user_carts[user_id].get(item_id, 0) + 1

    item = ITEMS.get(item_id) or VOUCHERS.get(item_id)
    await query.message.reply_text(f"✅ {item['name']} ба сабад илова шуд!")


async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    user_carts[user_id] = {}
    await query.message.reply_text("🗑️ Сабад пок карда шуд.")


async def addwish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return

    if item_id not in ITEMS and item_id not in VOUCHERS:
        return

    user_wishlist.setdefault(user_id, set()).add(item_id)
    item = ITEMS.get(item_id) or VOUCHERS.get(item_id)
    await query.message.reply_text(f"❤️ {item['name']} ба дилхоҳҳо илова шуд!")

    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return

    if item_id not in ITEMS and item_id not in VOUCHERS:
        return

    user_wishlist.setdefault(user_id, set()).add(item_id)
    item = ITEMS.get(item_id) or VOUCHERS.get(item_id)
    await query.message.reply_text(f"❤️ {item['name']} ба дилхоҳҳо илова шуд!")
    
async def open_wishlist_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    wishlist = user_wishlist.get(user_id, set())
    if not wishlist:
        await update.message.reply_text("❤️ Дилхоҳҳо холист.")
        return

    for i in list(wishlist):
        item = ITEMS.get(i) or VOUCHERS.get(i)
        if not item:
            continue
        buttons = [
            [InlineKeyboardButton("🛒 Ба сабад", callback_data=f"addcart_{i}"),
             InlineKeyboardButton("🗑️ Пок кардан", callback_data=f"removewish_{i}")]
        ]
        await update.message.reply_text(f"❤️ {item['name']} — {item['price']} TJS", reply_markup=InlineKeyboardMarkup(buttons))


async def removewish_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("🗑️ Аз дилхоҳҳо ҳазф шуд!")
    user_id = str(query.from_user.id)
    try:
        item_id = int(query.data.split("_")[1])
    except Exception:
        return
    if user_id in user_wishlist:
        user_wishlist[user_id].discard(item_id)
    try:
        await query.message.delete()
    except Exception:
        pass
        
# Cart and checkout
async def show_cart_from_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    cart = user_carts.get(user_id, {})

    if not cart:
        await update.message.reply_text("🛒 Сабад холист.")
        return

    text = "🛍 Маҳсулоти шумо:\n"
    total = 0

    for i, qty in cart.items():
        item = ITEMS.get(i) or VOUCHERS.get(i)
        if not item:
            continue
        subtotal = item["price"] * qty
        total += subtotal
        text += f"- {item['name']} x{qty} = {subtotal} TJS\n"

    text += f"\n💰 Ҳамагӣ: {total} TJS"

    buttons = [
        [
            InlineKeyboardButton("📦 Фармоиш додан", callback_data="checkout"),
            InlineKeyboardButton("🗑️ Пок кардан", callback_data="clear_cart"),
        ],
        [InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    cart = user_carts.get(user_id, {})

    if not cart:
        await query.message.reply_text("🛒 Сабад холист.")
        return

    # save cart snapshot for admin view
    context.user_data["pending_cart_items"] = cart.copy()

    await query.message.reply_text(
        "🎮 Лутфан ID-и бозии худро ворид кунед (фақат рақамҳо):"
    )

    context.user_data["awaiting_game_id"] = True
    context.user_data["pending_order_total"] = sum(
        (ITEMS.get(i) or VOUCHERS.get(i))["price"] * q
        for i, q in cart.items()
        if ITEMS.get(i) or VOUCHERS.get(i)
    )

async def get_game_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_game_id"):
        return

    game_id = update.message.text.strip()
    if not game_id.isdigit():
        await update.message.reply_text(
            "⚠️ Лутфан танҳо рақам ворид кунед (ID-и бозӣ бояд рақам бошад)."
        )
        return

    context.user_data["awaiting_game_id"] = False

    user_id = str(update.message.from_user.id)
    total = context.user_data.pop("pending_order_total", 0)

    order = _create_order_record(user_id, total)
    order["game_id"] = game_id
    order["status"] = "choose_payment"

    # save cart items inside order (for admin)
    order["items"] = context.user_data.pop("pending_cart_items", {})
    save_all()
    user_carts[user_id] = {}

    buttons = [
        [InlineKeyboardButton("💳 Пардохт VISA", callback_data=f"pay_visa_{order['id']}")],
        [InlineKeyboardButton("🏦 Пардохт SberBank", callback_data=f"pay_sber_{order['id']}")]
    ]

    await update.message.reply_text(
        f"Фармоиш №{order['id']}\n"
        f"🎮 ID: {game_id}\n"
        f"💰 Нархи умумӣ: {total} TJS\n\n"
        "Лутфан тарзи пардохтро интихоб кунед:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# Payment method selection
async def payment_method_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    if len(parts) < 3:
        await query.message.reply_text("⚠️ Формати маълумот нодуруст аст.")
        return

    method = parts[1]
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text("⚠️ Формати фармоиш нодуруст аст.")
        return

    card = VISA_NUMBER if method == "visa" else SBER_NUMBER
    method_name = "VISA" if method == "visa" else "SberBank"

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "awaiting_proof"
            order["payment_method"] = method_name
            save_all()

            await query.message.reply_text(
                f"💳 Тарзи пардохт: {method_name}\n"
                f"📌 Рақами корт/ҳисоб: {card}\n\n"
                "Пас аз пардохт, лутфан квитанцияро ҳамчун акс ё файл ба ин чат фиристед."
            )
            return

    await query.message.reply_text("⚠️ Фармоиш ёфт нашуд.")


# Receive payment proof
async def receive_payment_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    order = None
    for o in reversed(orders):
        if str(o.get("user_id")) == user_id and o.get("status") == "awaiting_proof":
            order = o
            break

    if not order:
        await update.message.reply_text("⚠️ Шумо ҳоло фармоиши интизори квитанция надоред.")
        return

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        is_photo = True
    elif update.message.document:
        file_id = update.message.document.file_id
        is_photo = False
    else:
        await update.message.reply_text("⚠️ Лутфан акс ё файл равон кунед!")
        return

    order["status"] = "proof_sent"
    order["proof_file"] = file_id
    save_all()

    # build items list for admin
    items_text = ""
    for i, qty in order.get("items", {}).items():
        item = ITEMS.get(i) or VOUCHERS.get(i)
        if not item:
            continue
        label = "Almaz" if i in ITEMS else "🎫 Ваучер"
        items_text += f"{label}: {item['name']} x{qty}\n"

    caption = (
        f"📦 Фармоиши №{order['id']}\n"
        f"👤 @{order.get('username') or order.get('user_name')}\n"
        f"🎮 ID: {order.get('game_id')}\n\n"
        f"{items_text}"
        f"\n💰 Ҳамагӣ: {order.get('total')} TJS\n"
        f"💳 Пардохт: {order.get('payment_method')}\n"
        f"📱 Телефон: {order.get('phone') or '—'}\n"
        f"🕒 {order.get('time')}"
    )

    buttons = [
        [
            InlineKeyboardButton("✅ Тасдиқ", callback_data=f"pay_confirm_{order['id']}"),
            InlineKeyboardButton("❌ Рад", callback_data=f"pay_reject_{order['id']}")
        ]
    ]

    for admin in ADMIN_IDS:
        try:
            if is_photo:
                await context.bot.send_photo(
                    chat_id=admin,
                    photo=file_id,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
            else:
                await context.bot.send_document(
                    chat_id=admin,
                    document=file_id,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
        except Exception:
            pass

    await update.message.reply_text(
        "✅ Квитанция қабул шуд! Мунтазир шавед, то админ тасдиқ кунад."
    )
    
# Admin confirm/reject for payments (pay_confirm_, pay_reject_)
async def admin_payment_verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split("_")
    # expected forms: pay_confirm_{id} or pay_reject_{id}
    if len(parts) < 3:
        await query.message.reply_text("⚠️ Формати маълумот нодуруст аст.")
        return

    action = parts[1]       # confirm / reject
    try:
        order_id = int(parts[2])
    except Exception:
        await query.message.reply_text("⚠️ Формати фармоиш нодуруст аст.")
        return

    for order in orders:
        if order["id"] == order_id:
            user_chat = int(order["user_id"])
            if action == "confirm":
                order["status"] = "confirmed"
                save_all()
                try:
                    await context.bot.send_message(user_chat, f"✅ Пардохти шумо барои фармоиши №{order_id} тасдиқ шуд ва ба ҳисобатон ворид шуд! Ташаккур.")
                except Exception:
                    pass
                await query.message.reply_text(f"✅ Фармоиш №{order_id} тасдиқ шуд.")
            else:
                order["status"] = "rejected"
                save_all()
                try:
                    await context.bot.send_message(user_chat, f"❌  Фармоиши шумо борои  №{order_id} рад шуд пардохт нашудааст! Лутфан бо админ тамос гиред.")
                except Exception:
                    pass
                await query.message.reply_text(f"❌ Фармоиш №{order_id} рад шуд.")
            return

    await query.message.reply_text("⚠️ Фармоиш ёфт нашуд.")


# Existing callback handlers for other flows remain (payment_accept/reject for another flow)
async def callback_payment_accept_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("payment_accept_"):
        parts = data.split("_")
        try:
            order_id = int(parts[2])
            user_id = int(parts[3])
        except Exception:
            await query.message.reply_text("⚠️ Формати маълумот нодуруст аст.")
            return
        for o in orders:
            if o["id"] == order_id and str(o["user_id"]) == str(user_id):
                o["status"] = "confirmed"
                save_all()
                try:
                    await context.bot.send_message(int(user_id), f"✅ Пардохти шумо барои фармоиши №{order_id} қабул шуд ва ба ҳисобатон ворид шуд! Ташаккур.")
                except Exception:
                    pass
                await query.message.reply_text(f"✅ Пардохти фармоиш №{order_id} тасдиқ шуд.")
                return
        await query.message.reply_text("Фармоиш ёфт нашуд.")

    elif data.startswith("payment_reject_"):
        parts = data.split("_")
        try:
            order_id = int(parts[2])
            user_id = int(parts[3])
        except Exception:
            await query.message.reply_text("⚠️ Формати маълумот нодуруст аст.")
            return
        for o in orders:
            if o["id"] == order_id and str(o["user_id"]) == str(user_id):
                o["status"] = "rejected"
                save_all()
                try:
                    await context.bot.send_message(int(user_id), f"❌ Пардохти шумо барои фармоиши №{order_id} рад шуд. Лутфан бо админ тамос гиред.")
                except Exception:
                    pass
                await query.message.reply_text(f"❌ Пардохти фармоиш №{order_id} рад шуд.")
                return
        await query.message.reply_text("Фармоиш ёфт нашуд.")


# Free UC system
async def free_uc_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat if update.message else update.callback_query.message.chat
    from_user = update.message.from_user if update.message else update.callback_query.from_user
    user_id = str(from_user.id)

    if user_id not in users_data:
        await chat.send_message("⚠️ Аввал /start кунед.")
        return

    # Check subscription (best-effort; may fail for private channels)
    subscribed = False
    try:
        member = await context.bot.get_chat_member(FREE_UC_CHANNEL, int(user_id))
        subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        subscribed = False

    buttons = []
    if subscribed:
        buttons.append([InlineKeyboardButton("🎲 Гирифтани UC-и рӯзона", callback_data="daily_uc")])
        buttons.append([InlineKeyboardButton("📊 UC-и ҷамъшуда", callback_data="my_uc")])
        buttons.append([
            InlineKeyboardButton("🎁 60 UC", callback_data="claim_60"),
            InlineKeyboardButton("🎁 325 UC", callback_data="claim_325"),
        ])
    else:
        channel_url = f"https://t.me/{FREE_UC_CHANNEL.lstrip('@')}"
        buttons.append([InlineKeyboardButton("📢 Обуна шудан", url=channel_url)])
        buttons.append([InlineKeyboardButton("🔄 Санҷиш", callback_data="check_sub_ucfree")])

    buttons.append([InlineKeyboardButton("🔗 Даъвати дӯстон", callback_data="invite_link")])
    await chat.send_message("🎁 Менюи UC ройгон:", reply_markup=InlineKeyboardMarkup(buttons))


async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await free_uc_menu(update, context)


async def daily_uc_roll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    user = users_data.get(user_id)
    if not user:
        await q.message.reply_text("⚠️ Аввал /start кунед.")
        return

    now = datetime.datetime.now()
    last = user.get("last_daily_uc")
    if last:
        try:
            last_dt = datetime.datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
            if (now - last_dt).total_seconds() < 24 * 3600:
                remaining = int((24 * 3600 - (now - last_dt).total_seconds()) // 3600)
                await q.message.reply_text(f"⏳ Шумо аллакай UC гирифтед. Ба шумо боз {remaining} соат мондааст.")
                return
        except Exception:
            pass

    roll = random.choices([1, 2, 3, 4, 5], weights=[70, 20, 7, 2, 1])[0]
    user["free_uc"] = user.get("free_uc", 0) + roll
    user["last_daily_uc"] = now.strftime("%Y-%m-%d %H:%M:%S")
    users_data[user_id] = user
    save_all()
    await q.message.reply_text(f"🎉 Шумо {roll} UC гирифтед!\n📊 Ҳамагӣ: {user['free_uc']} UC")


async def my_uc_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user_id = str(q.from_user.id)
    user = users_data.get(user_id, {})
    amount = user.get("free_uc", 0)
    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 60 UC", callback_data="claim_60")],
        [InlineKeyboardButton("🎁 325 UC", callback_data="claim_325")],
    ])
    await q.message.reply_text(f"📊 Шумо доред: {amount} UC", reply_markup=btn)


async def claim_uc_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    needed = 60 if data == "claim_60" else 325 if data == "claim_325" else None
    if not needed:
        return
    user_id = str(q.from_user.id)
    user = users_data.get(user_id, {})
    if user.get("free_uc", 0) < needed:
        await q.message.reply_text(f"❌ Шумо UC кофӣ надоред. Шумо доред: {user.get('free_uc', 0)} UC")
        return
    context.user_data["awaiting_free_id"] = needed
    await q.message.reply_text("🎮 Лутфан ID-и PUBG-ро ворид кунед (8–15 рақам):")


async def get_free_uc_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_free_id" not in context.user_data:
        return
    t = update.message.text.strip()
    if not t.isdigit() or not (8 <= len(t) <= 15):
        await update.message.reply_text("⚠️ Танҳо рақам, аз 8 то 15 рақам! Лутфан дубора кӯшиш кунед.")
        return
    amount = context.user_data.pop("awaiting_free_id")
    user_id = str(update.message.from_user.id)
    user = users_data.get(user_id)
    if not user:
        await update.message.reply_text("⚠️ Аввал /start кунед.")
        return

    user["free_uc"] = max(0, user.get("free_uc", 0) - amount)
    users_data[user_id] = user
    save_all()

    order_id = random.randint(10000, 99999)
    order = {
        "id": order_id,
        "user_id": user_id,
        "username": user.get("username"),
        "phone": user.get("phone"),
        "total": 0,
        "type": "free_uc",
        "pack": amount,
        "game_id": t,
        "status": "pending",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    orders.append(order)
    save_all()

    for admin in ADMIN_IDS:
        try:
            btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Тасдиқ", callback_data=f"admin_confirm_free_{order_id}"),
                    InlineKeyboardButton("❌ Рад", callback_data=f"admin_reject_free_{order_id}"),
                ]
            ])
            await context.bot.send_message(
                admin,
                f"📦 Фармоиши UC ройгон №{order_id}\n👤 @{order['username']}\n🎮 ID: {t}\n🎁 Пакет: {amount} UC",
                reply_markup=btn,
            )
        except Exception:
            pass

    await update.message.reply_text(f"🎁 Дархости {amount} UC ба админ фиристода шуд! (Фармоиш №{order_id})")


async def admin_confirm_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        order_id = int(q.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id and o.get("type") == "free_uc":
            if o["status"] != "pending":
                await q.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "confirmed"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), f"✅ Дархости UC (№{order_id}) тасдиқ шуд! Ташаккур.")
            except Exception:
                pass
            await q.message.reply_text("✅ Тасдиқ шуд.")
            return
    await q.message.reply_text("Фармоиш ёфт нашуд.")


async def admin_reject_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        order_id = int(q.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id and o.get("type") == "free_uc":
            o["status"] = "rejected"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), f"❌ Дархост (№{order_id}) рад шуд. Лутфан бо админ тамос гиред.")
            except Exception:
                pass
            await q.message.reply_text("❌ Рад шуд.")
            return
    await q.message.reply_text("Фармоиш ёфт нашуд.")


# Admin confirm/reject for paid orders (original flow)
async def admin_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        order_id = int(query.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id:
            if o["status"] != "pending":
                await query.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "awaiting_payment"
            save_all()
            try:
                await context.bot.send_message(
                    int(o["user_id"]),
                    f"💳 Барои анҷом додани пардохт, лутфан ба рақами VISA зер пардохт кунед:\n\n🔹 {VISA_NUMBER}\n\nПас аз пардохт, скриншоти тасдиқро ба ин ҷо фиристед 📸",
                )
            except Exception:
                pass
            await query.message.reply_text(f"📨 Рақами VISA ба @{o['username'] or o['user_name']} фиристода шуд.")
            return
    await query.message.reply_text("Фармоиш ёфт нашуд.")


async def admin_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        order_id = int(query.data.split("_")[-1])
    except Exception:
        return
    for o in orders:
        if o["id"] == order_id:
            if o["status"] != "pending":
                await query.message.reply_text(f"Фармоиш аллакай дар ҳолати: {o['status']}")
                return
            o["status"] = "rejected"
            save_all()
            try:
                await context.bot.send_message(int(o["user_id"]), f"❌ Фармоиши шумо №{o['id']} рад шуд. Лутфан бо админ тамос гиред.")
            except Exception:
                pass
            await query.message.reply_text(f"❌ Фармоиш №{order_id} рад шуд.")
            return
    await query.message.reply_text("Фармоиш ёфт нашуд.")


# Invite link
async def invite_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    user = q.from_user
    uid = str(user.id)
    try:
        bot = await context.bot.get_me()
        bot_username = bot.username
    except Exception:
        await q.message.reply_text("⚠️ Хато: бот номи худро ёфта натавонист.")
        return
    invite_url = f"https://t.me/{bot_username}?start=invite_{uid}"
    await q.message.reply_text(
        "🔗 Ин линкро ба дӯстонат фирист:\n\n" + invite_url + "\n\nҲар дӯсте, ки сабт мешавад → ту 2 UC мегирӣ!"
    )


# Admin panel (single implementation)
async def admin_panel_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)

    if data == "admin_panel":
        keyboard = [
            [InlineKeyboardButton("👤 Корбарон", callback_data="admin_users")],
            [InlineKeyboardButton("📦 Заказҳо", callback_data="admin_orders")],
            [InlineKeyboardButton("📢 Расонидани паём", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")],
        ]
        await query.message.edit_text(
            "⚙️ *Панели Администратор*\nДар ин ҷо ту тамоми мағоза ва корбарҳоро идора мекунӣ.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_users":
        if not users_data:
            text = "📋 Ҳоло ҳеҷ корбар нест."
        else:
            text = "📋 *Рӯйхати корбарон:*\n\n"
            for uid, u in users_data.items():
                text += f"• {u.get('name','—')} — {u.get('phone','—')} (id: {uid})\n"
        await query.message.edit_text(
            text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Бозгашт", callback_data="admin_panel")]])
        )
        return

    if data == "admin_orders":
        if not orders:
            text = "❗ Ҳоло ҳеҷ заказ нест."
        else:
            text = "📦 *Рӯйхати заказҳо:*\n\n"
            for o in orders:
                text += f"#{o['id']} — @{o.get('username') or o.get('user_name','-')} — {o.get('total', o.get('pack',0))} — {o['status']}\n"
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Бозгашт", callback_data="admin_panel")]]))
        return

    if data == "admin_broadcast":
        broadcast_mode[user_id] = True
        await query.message.edit_text("✏️ Матнро фирист ", parse_mode="Markdown")
        return


# Text handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.message.from_user.id)

    # Broadcast mode
    if broadcast_mode.get(user_id):
        msg = text
        count = 0
        for uid in list(users_data.keys()):
            try:
                await context.bot.send_message(int(uid), f"📣 Паём аз админ:\n\n{msg}")
                count += 1
            except Exception:
                pass
        await update.message.reply_text(f"✅ Паём ба {count} корбар фиристода шуд.")
        broadcast_mode[user_id] = False
        return

    # Menu commands
    if text == "🛍 Мағоза":
        await catalog_handler(update, context)
    elif text == "❤️ Дилхоҳҳо":
        await open_wishlist_from_text(update, context)
    elif text == "🛒 Сабад":
        await show_cart_from_text(update, context)
    elif text == "ℹ Маълумот":
        await update.message.reply_text(ADMIN_INFO)
    elif text == "💬 Профили админ":
        await update.message.reply_text(
        "Профили админ:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📸 Instagram", url=ADMIN_INSTAGRAM)],
            [InlineKeyboardButton("✈️ Telegram", url=ADMIN_TELEGRAM)],
        ]),
    )
    elif text == "👑 Панели админ" and int(user_id) in ADMIN_IDS:
        buttons = [
            [InlineKeyboardButton("📋 Рӯйхати корбарон", callback_data="admin_users"), InlineKeyboardButton("📦 Фармоишҳо", callback_data="admin_orders")],
            [InlineKeyboardButton("📣 Паём ба корбарон", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")],
        ]
        await update.message.reply_text("👑 Панели админ:", reply_markup=InlineKeyboardMarkup(buttons))
    elif text == "🎁 UC ройгон":
        await free_uc_menu(update, context)
    else:
        await update.message.reply_text("🤖 Лутфан аз тугмаҳои меню истифода баред.")


# Text router for awaiting inputs
async def text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # First, check if user is answering the math challenge
    if context.user_data.get("awaiting_math_answer"):
        await _check_math_answer(update, context)
        return

    if context.user_data.get("awaiting_game_id"):
        await get_game_id(update, context)
        return
    if "awaiting_free_id" in context.user_data:
        await get_free_uc_id(update, context)
        return
    await handle_text(update, context)
    
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query or not query.data:
        return

    data = query.data

    # ---------------- Admin panel ----------------
    if data in ["admin_panel", "admin_users", "admin_orders", "admin_broadcast", "back_admin"]:
        await admin_panel_main(update, context)
        return

    # ---------------- Catalog ----------------
    if data == "catalog_uc":
        await catalog_uc_callback(update, context)
        return

    if data == "catalog_voucher":
        await catalog_voucher_callback(update, context)
        return

    # Almaz product page
    if data.startswith("select_") and not data.startswith("select_voucher_"):
        await select_item_callback(update, context)
        return

    # Voucher product page
    if data.startswith("select_voucher_"):
        await select_voucher_callback(update, context)
        return

    # ---------------- Cart / Wishlist ----------------
    if data.startswith("addcart_"):
        await addcart_callback(update, context)
        return

    if data.startswith("addwish_"):
        await addwish_callback(update, context)
        return

    if data.startswith("removewish_"):
        await removewish_callback(update, context)
        return

    if data == "clear_cart":
        await clear_cart_callback(update, context)
        return

    if data == "checkout":
        await checkout_callback(update, context)
        return

    if data == "back_main":
        uid = str(query.from_user.id)
        await show_main_menu(query.message.chat, uid)
        return

    # ---------------- Payments ----------------
    # Legacy accept / reject
    if data.startswith("payment_accept_") or data.startswith("payment_reject_"):
        await callback_payment_accept_reject(update, context)
        return

    # Payment method selection
    if data.startswith("pay_visa_") or data.startswith("pay_sber_"):
        await payment_method_callback(update, context)
        return

    # Admin confirm / reject proofs
    if data.startswith("pay_confirm_") or data.startswith("pay_reject_"):
        await admin_payment_verify(update, context)
        return

    # ---------------- Free UC ----------------
    if data == "check_sub_ucfree":
        await check_sub_callback(update, context)
        return

    if data == "daily_uc":
        await daily_uc_roll(update, context)
        return

    if data == "my_uc":
        await my_uc_info(update, context)
        return

    if data in ["claim_60", "claim_325"]:
        await claim_uc_button(update, context)
        return

    if data.startswith("admin_confirm_free_"):
        await admin_confirm_free(update, context)
        return

    if data.startswith("admin_reject_free_"):
        await admin_reject_free(update, context)
        return

    if data == "invite_link":
        await invite_link_callback(update, context)
        return

    # ---------------- Unknown ----------------
    await query.answer()

# Commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 Фармонҳо: /start, /help, /about, /users (админ)")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADMIN_INFO)


async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.message.from_user.id) not in ADMIN_IDS:
        await update.message.reply_text("🚫 Танҳо админ!")
        return
    if not users_data:
        await update.message.reply_text("Ҳеҷ корбар сабт нашудааст.")
        return
    text = "📋 Рӯйхати корбарон:\n\n"
    for u in users_data.values():
        text += f"👤 {u.get('name','—')} — {u.get('phone','—')} (id: {u.get('id')})\n"
    await update.message.reply_text(text)


# Extra command wrappers
async def catalog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await catalog_handler(update, context)


async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_cart_from_text(update, context)


async def wishlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_wishlist_from_text(update, context)


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ADMIN_INFO)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = int(update.message.from_user.id)
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("🚫 Танҳо админ!")
        return
    buttons = [
        [InlineKeyboardButton("📋 Рӯйхати корбарон", callback_data="admin_users"), InlineKeyboardButton("📦 Фармоишҳо", callback_data="admin_orders")],
        [InlineKeyboardButton("📣 Паём ба корбарон", callback_data="admin_broadcast")],
        [InlineKeyboardButton("⬅️ Бозгашт", callback_data="back_main")],
    ]
    await update.message.reply_text("👑 Панели админ:", reply_markup=InlineKeyboardMarkup(buttons))


# Main

def main():
    if TOKEN == "REPLACE_WITH_YOUR_BOT_TOKEN":
        print("Please set TOKEN in the script before running.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("users", users_command))

    # Extra commands
    app.add_handler(CommandHandler("catalog", catalog_command))
    app.add_handler(CommandHandler("cart", cart_command))
    app.add_handler(CommandHandler("wishlist", wishlist_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("admin", admin_command))

    # Contact handler
    app.add_handler(MessageHandler(filters.CONTACT, get_contact))

    # CallbackQuery (single router)
    app.add_handler(CallbackQueryHandler(callback_router))

    # Photos & Documents (payment proofs)
    app.add_handler(MessageHandler((filters.PHOTO | filters.Document.ALL) & (~filters.COMMAND), receive_payment_photo))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_router))

    print("✅ UCstore бот фаъол шуд!")
    app.run_polling()


if __name__ == "__main__":
    main()
