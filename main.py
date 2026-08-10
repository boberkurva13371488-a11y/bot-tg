import telebot
import json
import os
import re
from datetime import datetime, timedelta
from collections import Counter

# ============================================================
# НАСТРОЙКИ
# ============================================================

TOKEN = "8812212137:AAFDUsgKmlhoKsyN0FaXJl1y21AxyDTytl4"

# Твой Telegram ID
ADMIN_IDS = {
    8780322706
}

MESSAGES_FILE = "messages.json"
VIOLATIONS_FILE = "violations.json"

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")


# ============================================================
# ПРАВИЛА
# ============================================================

RULES = {
    "1.1": {
        "name": "Оскорбления и неадекватное поведение",
        "punishment": "Мут 1 час"
    },
    "1.2": {
        "name": "Оскорбление родных",
        "punishment": "Мут 10 часов"
    },
    "1.3": {
        "name": "Спам / флуд / рейд",
        "punishment": "Мут 2 часа"
    },
    "1.4": {
        "name": "Контент 18+",
        "punishment": "Мут навсегда"
    },
    "1.5": {
        "name": "Продажа / покупка",
        "punishment": "Мут 1 день"
    },
    "1.6": {
        "name": "Реклама",
        "punishment": "Мут 7 дней"
    },
    "1.7": {
        "name": "Попрошайничество",
        "punishment": "Мут 15 минут"
    },
    "1.8": {
        "name": "Упоминания",
        "punishment": "Мут 15 минут"
    },
    "1.9": {
        "name": "Задания / созыв в ЛС",
        "punishment": "Мут 7 дней"
    },
    "2.0": {
        "name": "Скам",
        "punishment": "Бан навсегда"
    },
    "2.1": {
        "name": "Политика",
        "punishment": "Мут 10 часов"
    },
    "2.2": {
        "name": "Угрозы",
        "punishment": "Мут 30 дней / бан навсегда"
    },
    "2.3": {
        "name": "Религия",
        "punishment": "Мут 7 дней"
    },
    "2.4": {
        "name": "Слив личной информации",
        "punishment": "Бан навсегда"
    },
    "2.5": {
        "name": "Спорные шутки",
        "punishment": "Мут 1 день"
    },
    "2.6": {
        "name": "Реклама в личных сообщениях",
        "punishment": "Бан 7 дней / навсегда"
    },
    "2.7": {
        "name": "Долги",
        "punishment": "Мут 1 час"
    },
    "2.8": {
        "name": "Созыв в ЛС",
        "punishment": "Мут 5 часов"
    },
    "2.9": {
        "name": "Попрошайничество у владельца проекта",
        "punishment": "Мут 1 час"
    }
}


# ============================================================
# СЛОВАРИ И ПАТТЕРНЫ
# ============================================================

PROFANITY_PATTERNS = [
    r"\bхуй\w*",
    r"\bху[йияе]\w*",
    r"\bпизд\w*",
    r"\bеб\w*",
    r"\bёб\w*",
    r"\bебан\w*",
    r"\bбляд\w*",
    r"\bбля\w*",
    r"\bсука\w*",
    r"\bсучк\w*",
    r"\bмраз\w*",
    r"\bгандон\w*",
    r"\bдолбоеб\w*",
    r"\bдолбаеб\w*",
    r"\bдебил\w*",
    r"\bидиот\w*",
    r"\bтупиц\w*",
    r"\bкретин\w*",
    r"\bурод\w*",
    r"\bтвар\w*",
]

RELATIVE_PATTERNS = [
    r"\bмать\b",
    r"\bмам[аеуыой]\b",
    r"\bмамк[аеуы]\b",
    r"\bмамаша\b",
    r"\bотец\b",
    r"\bпап[аеуыой]\b",
    r"\bпапаш[аеуы]\b",
    r"\bбат[ья]?\b",
    r"\bсын\b",
    r"\bдочь\b",
    r"\bдочк[аеуы]\b",
    r"\bбрат\b",
    r"\bсестр[аеы]\b",
    r"\bродител\w*",
]

THREAT_PATTERNS = [
    r"\bубью\b",
    r"\bубивать\b",
    r"\bубить\b",
    r"\bзастрел\w*",
    r"\bзареж\w*",
    r"\bсломаю\b",
    r"\bпокалеч\w*",
    r"\bнайду\s+тебя\b",
    r"\bприеду\s+к\s+тебе\b",
    r"\bтебе\s+конец\b",
    r"\bпожалеешь\b",
]

POLITICS_PATTERNS = [
    r"\bпрезидент\w*",
    r"\bпутин\b",
    r"\bтрамп\b",
    r"\bзеленск\w*",
    r"\bвойн[аеы]\b",
    r"\bвыборы\b",
    r"\bвыборов\b",
    r"\bдепутат\w*",
    r"\bправительств\w*",
    r"\bполитик\w*",
    r"\bоппозици\w*",
    r"\bсанкци\w*",
]

RELIGION_PATTERNS = [
    r"\bбог\b",
    r"\bаллах\b",
    r"\bхрист\w*",
    r"\bислам\w*",
    r"\bхристиан\w*",
    r"\bправослав\w*",
    r"\bкатолик\w*",
    r"\bцерков\w*",
    r"\bмечет\w*",
    r"\bрелиги\w*",
]

ADULT_PATTERNS = [
    r"\bпорно\w*",
    r"\bпорн\w*",
    r"\bэротик\w*",
    r"\bсекс\w*",
    r"\bинтим\w*",
    r"\bxxx\b",
    r"\bnsfw\b",
    r"\b18\+\b",
    r"\bonlyfans\b",
]

SELL_PATTERNS = [
    r"\bпродам\b",
    r"\bпродаю\b",
    r"\bпродажа\b",
    r"\bкуплю\b",
    r"\bкупить\b",
    r"\bпокупка\b",
    r"\bцена\b",
    r"\bрублей\b",
    r"\bруб\b",
    r"₽",
    r"\bденьги\b",
    r"\bоплата\b",
    r"\bперевод\b",
]

AD_PATTERNS = [
    r"https?://",
    r"www\.",
    r"\bподписывайтесь\b",
    r"\bподписывайся\b",
    r"\bпереходи\b",
    r"\bпереходите\b",
    r"\bнаш\s+канал\b",
    r"\bнаш\s+бот\b",
    r"\bнаш\s+проект\b",
    r"\bрозыгрыш\b",
    r"\bпромокод\b",
]

BEGGING_PATTERNS = [
    r"\bнакидай\w*",
    r"\bнакинуть\b",
    r"\bдонат\b",
    r"\bдонать\b",
    r"\bзадонать\b",
    r"\bпомогите\s+деньг",
    r"\bдайте\s+денег\b",
    r"\bскиньте\s+денег\b",
    r"\bскинь\s+денег\b",
    r"\bможно\s+денег\b",
]

SCAM_PATTERNS = [
    r"\bгарантированн\w*\s+заработ",
    r"\bлегк\w*\s+заработ",
    r"\bбыстр\w*\s+заработ",
    r"\bинвестиц\w*",
    r"\bудвою\b",
    r"\bудвоить\b",
    r"\bприбыль\b",
    r"\bбез\s+риска\b",
    r"\b100%\s*доход",
]

DM_PATTERNS = [
    r"\bв\s+лс\b",
    r"\bв\s+личку\b",
    r"\bличку\b",
    r"\bнапиши\s+мне\b",
    r"\bпиши\s+в\s+лс\b",
    r"\bотпиши\s+в\s+лс\b",
    r"\bпм\b",
]

SUICIDE_PATTERNS = [
    r"\bсуицид\w*",
    r"\bсамоубийств\w*",
    r"\bпокончу\s+с\s+собой\b",
    r"\bповешусь\b",
    r"\bумереть\b",
]

VIOLENCE_PATTERNS = [
    r"\bубью\b",
    r"\bубить\b",
    r"\bзареж\w*",
    r"\bзастрел\w*",
    r"\bвзорв\w*",
    r"\bизобью\b",
]

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d[\d\s\-\(\)]{8,}\d)(?!\d)"
)

MENTION_PATTERN = re.compile(
    r"@[A-Za-z0-9_]{4,32}"
)

TELEGRAM_LINK_PATTERN = re.compile(
    r"(?:https?://)?t\.me/[A-Za-z0-9_+/?-]+",
    re.IGNORECASE
)


# ============================================================
# РАБОТА С ФАЙЛАМИ
# ============================================================

def load_json(filename, default):
    if not os.path.exists(filename):
        return default

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


def load_messages():
    return load_json(MESSAGES_FILE, [])


def load_violations():
    return load_json(VIOLATIONS_FILE, [])


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def normalize_text(text):
    if not text:
        return ""

    text = text.lower()

    compact = re.sub(
        r"[\s\W_]+",
        "",
        text
    )

    return text, compact


def find_patterns(text, patterns):
    found = []

    for pattern in patterns:
        try:
            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                found.append(pattern)
        except re.error:
            pass

    return found


def username_of(user):
    if user.username:
        return "@" + user.username

    full_name = " ".join(
        x
        for x in [
            user.first_name,
            user.last_name
        ]
        if x
    )

    return full_name or str(user.id)


def message_link(message):
    try:
        if message.chat.type == "private":
            return None

        if message.chat.username:
            return (
                f"https://t.me/"
                f"{message.chat.username}/"
                f"{message.message_id}"
            )

        chat_id = str(message.chat.id)

        if chat_id.startswith("-100"):
            internal_id = chat_id[4:]

            return (
                f"https://t.me/c/"
                f"{internal_id}/"
                f"{message.message_id}"
            )

    except Exception:
        pass

    return None


def is_admin(message):
    if not ADMIN_IDS:
        return True

    return message.from_user.id in ADMIN_IDS


# ============================================================
# УВЕДОМЛЕНИЕ АДМИНА
# ============================================================

def notify_admin(message_data, violation):

    rule = violation["rule"]
    rule_info = RULES[rule]

    username = (
        "@" + message_data["username"]
        if message_data["username"]
        else message_data["display_name"]
    )

    chat_name = (
        message_data["chat_title"]
        or "Личная переписка"
    )

    text = (
        "🚨 <b>НАЙДЕНО НАРУШЕНИЕ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"📌 <b>Правило:</b> "
        f"{rule} — {rule_info['name']}\n"

        f"👤 <b>Пользователь:</b> "
        f"{username}\n"

        f"🆔 <b>ID пользователя:</b> "
        f"<code>{message_data['user_id']}</code>\n"

        f"💬 <b>Чат:</b> "
        f"{chat_name}\n"

        f"🕐 <b>Дата:</b> "
        f"{message_data['date']}\n\n"

        f"⚠️ <b>Причина:</b>\n"
        f"{violation['reason']}\n\n"

        f"🔨 <b>Наказание:</b>\n"
        f"{rule_info['punishment']}\n\n"

        f"💬 <b>Сообщение:</b>\n"
        f"<code>{message_data['text'][:1000]}</code>"
    )

    if message_data.get("link"):
        text += (
            "\n\n"
            f'🔗 <a href="{message_data["link"]}">'
            "Открыть сообщение</a>"
        )

    for admin_id in ADMIN_IDS:

        try:

            bot.send_message(
                admin_id,
                text,
                disable_web_page_preview=True
            )

            print(
                f"📨 Уведомление отправлено "
                f"администратору {admin_id}"
            )

        except Exception as e:

            print(
                f"❌ Ошибка отправки уведомления "
                f"{admin_id}: {e}"
            )


# ============================================================
# АНАЛИЗ СООБЩЕНИЯ
# ============================================================

def analyze_message(text):

    violations = []

    if not text:
        return violations

    text_lower = text.lower()

    # 1.1

    if find_patterns(
        text_lower,
        PROFANITY_PATTERNS
    ):

        violations.append({
            "rule": "1.1",
            "reason":
                "Обнаружена ненормативная "
                "лексика / оскорбление."
        })

    # 1.2

    relative = find_patterns(
        text_lower,
        RELATIVE_PATTERNS
    )

    profanity = find_patterns(
        text_lower,
        PROFANITY_PATTERNS
    )

    if relative and profanity:

        violations.append({
            "rule": "1.2",
            "reason":
                "В сообщении обнаружено "
                "упоминание родственника "
                "в контексте возможного "
                "оскорбления."
        })

    family_insults = [
        r"твоя\s+мать",
        r"твою\s+мать",
        r"твоя\s+мам",
        r"твою\s+мам",
        r"твой\s+отец",
        r"твой\s+пап",
        r"твоя\s+сестр",
        r"твой\s+брат",
    ]

    if (
        find_patterns(
            text_lower,
            family_insults
        )
        and profanity
    ):

        violations.append({
            "rule": "1.2",
            "reason":
                "Обнаружено возможное "
                "оскорбление родственника."
        })

    # 1.4

    if find_patterns(
        text_lower,
        ADULT_PATTERNS
    ):

        violations.append({
            "rule": "1.4",
            "reason":
                "Обнаружены признаки "
                "контента 18+."
        })

    # 1.5

    if find_patterns(
        text_lower,
        SELL_PATTERNS
    ):

        violations.append({
            "rule": "1.5",
            "reason":
                "Обнаружены признаки "
                "продажи/покупки."
        })

    # 1.6

    if find_patterns(
        text_lower,
        AD_PATTERNS
    ):

        violations.append({
            "rule": "1.6",
            "reason":
                "Обнаружены признаки "
                "рекламы или продвижения."
        })

    # 1.7

    if find_patterns(
        text_lower,
        BEGGING_PATTERNS
    ):

        violations.append({
            "rule": "1.7",
            "reason":
                "Обнаружена просьба "
                "о деньгах/накидах."
        })

    # 1.9

    if find_patterns(
        text_lower,
        DM_PATTERNS
    ):

        violations.append({
            "rule": "1.9",
            "reason":
                "Обнаружен призыв перейти "
                "в личные сообщения."
        })

    # 2.0

    if find_patterns(
        text_lower,
        SCAM_PATTERNS
    ):

        violations.append({
            "rule": "2.0",
            "reason":
                "Обнаружены признаки "
                "потенциального скама "
                "или сомнительного заработка."
        })

    # 2.1

    if find_patterns(
        text_lower,
        POLITICS_PATTERNS
    ):

        violations.append({
            "rule": "2.1",
            "reason":
                "Обнаружена политическая тематика."
        })

    # 2.2

    if find_patterns(
        text_lower,
        THREAT_PATTERNS
    ):

        violations.append({
            "rule": "2.2",
            "reason":
                "Обнаружена возможная угроза."
        })

    # 2.3

    if find_patterns(
        text_lower,
        RELIGION_PATTERNS
    ):

        negative = (
            profanity
            or find_patterns(
                text_lower,
                [
                    r"\bненавиж\w*",
                    r"\bоскорб\w*",
                    r"\bуниж\w*",
                    r"\bсме[яе]\w*",
                    r"\bтуп\w*",
                ]
            )
        )

        if negative:

            violations.append({
                "rule": "2.3",
                "reason":
                    "Обнаружено возможное "
                    "унижение/оскорбление религии."
            })

    # 2.4

    if PHONE_PATTERN.search(text):

        violations.append({
            "rule": "2.4",
            "reason":
                "Обнаружен потенциальный "
                "номер телефона."
        })

    personal_patterns = [
        r"\bпаспорт\b",
        r"\bпаспортные\s+данные\b",
        r"\bфио\b",
        r"\bполное\s+имя\b",
        r"\bадрес\s+проживания\b",
        r"\bдомашний\s+адрес\b",
    ]

    if find_patterns(
        text_lower,
        personal_patterns
    ):

        violations.append({
            "rule": "2.4",
            "reason":
                "Обнаружено возможное "
                "разглашение личной информации."
        })

    # 2.5

    controversial = (
        find_patterns(
            text_lower,
            SUICIDE_PATTERNS
        )
        or find_patterns(
            text_lower,
            VIOLENCE_PATTERNS
        )
    )

    if controversial:

        violations.append({
            "rule": "2.5",
            "reason":
                "Обнаружена потенциально "
                "спорная шутка о суициде "
                "или насилии."
        })

    # 2.7

    debt_patterns = [
        r"\bдай\s+в\s+долг\b",
        r"\bдайте\s+в\s+долг\b",
        r"\bодолжи\b",
        r"\bодолжите\b",
        r"\bзанять\s+денег\b",
        r"\bзанять\s+деньги\b",
    ]

    if find_patterns(
        text_lower,
        debt_patterns
    ):

        violations.append({
            "rule": "2.7",
            "reason":
                "Обнаружена просьба "
                "дать деньги в долг."
        })

    # 2.8

    if find_patterns(
        text_lower,
        DM_PATTERNS
    ):

        violations.append({
            "rule": "2.8",
            "reason":
                "Обнаружен призыв перейти "
                "в личные сообщения."
        })

    # 2.9

    owner_patterns = [
        r"\bвладелец\b",
        r"\bсоздатель\b",
        r"\bадмин\b",
        r"\bадминистраци\w*",
        r"\bнакидай\b",
        r"\bпромокод\b",
        r"\bраздач\w*",
    ]

    if (
        find_patterns(
            text_lower,
            owner_patterns
        )
        and find_patterns(
            text_lower,
            BEGGING_PATTERNS
        )
    ):

        violations.append({
            "rule": "2.9",
            "reason":
                "Возможная просьба "
                "о накидах/раздаче/промокоде."
        })

    return violations


# ============================================================
# СОХРАНЕНИЕ СООБЩЕНИЯ
# ============================================================

def save_message(message):

    messages = load_messages()

    text = (
        message.text
        or message.caption
        or ""
    )

    data = {

        "message_id":
            message.message_id,

        "chat_id":
            message.chat.id,

        "chat_title":
            getattr(
                message.chat,
                "title",
                None
            ),

        "chat_username":
            getattr(
                message.chat,
                "username",
                None
            ),

        "user_id":
            message.from_user.id,

        "username":
            message.from_user.username,

        "display_name":
            username_of(
                message.from_user
            ),

        "date":
            datetime.fromtimestamp(
                message.date
            ).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "text":
            text,

        "has_photo":
            bool(message.photo),

        "has_video":
            bool(message.video),

        "has_document":
            bool(message.document),

        "has_sticker":
            bool(message.sticker),

        "link":
            message_link(message)
    }

    messages.append(data)

    save_json(
        MESSAGES_FILE,
        messages
    )

    return data


# ============================================================
# СОХРАНЕНИЕ НАРУШЕНИЯ
# ============================================================

def save_violation(
    message_data,
    violation
):

    violations = load_violations()

    rule = violation["rule"]

    record = {

        "id":
            len(violations) + 1,

        "rule":
            rule,

        "rule_name":
            RULES[rule]["name"],

        "punishment":
            RULES[rule]["punishment"],

        "reason":
            violation["reason"],

        "message_id":
            message_data["message_id"],

        "chat_id":
            message_data["chat_id"],

        "chat_title":
            message_data["chat_title"],

        "user_id":
            message_data["user_id"],

        "username":
            message_data["username"],

        "display_name":
            message_data["display_name"],

        "date":
            message_data["date"],

        "text":
            message_data["text"],

        "link":
            message_data["link"]
    }

    violations.append(record)

    save_json(
        VIOLATIONS_FILE,
        violations
    )

    return record


# ============================================================
# АНАЛИЗ + СОХРАНЕНИЕ + УВЕДОМЛЕНИЕ
# ============================================================

def process_message(message):

    data = save_message(message)

    text = data["text"]

    found = analyze_message(text)

    saved = []

    for violation in found:

        saved_violation = save_violation(
            data,
            violation
        )

        saved.append(
            saved_violation
        )

        # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ ТЕБЕ
        notify_admin(
            data,
            violation
        )

    return data, saved


# ============================================================
# АНАЛИЗ СПАМА
# ============================================================

def analyze_spam():

    messages = load_messages()

    violations = []

    users = {}

    for msg in messages:

        users.setdefault(
            msg["user_id"],
            []
        ).append(msg)

    for user_id, user_messages in users.items():

        user_messages.sort(
            key=lambda x: x["date"]
        )

        for i in range(
            len(user_messages)
        ):

            current = user_messages[i]

            try:

                current_time = (
                    datetime.strptime(
                        current["date"],
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

            except Exception:
                continue

            window = []

            for msg in user_messages[i:]:

                try:

                    msg_time = (
                        datetime.strptime(
                            msg["date"],
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )

                except Exception:
                    continue

                if (
                    msg_time - current_time
                    <= timedelta(seconds=30)
                ):

                    window.append(msg)

                else:
                    break

            if len(window) >= 6:

                first = window[0]

                violation = {
                    "rule": "1.3",
                    "reason":
                        f"Обнаружен возможный флуд: "
                        f"{len(window)} сообщений "
                        f"за 30 секунд."
                }

                record = save_violation(
                    first,
                    violation
                )

                notify_admin(
                    first,
                    violation
                )

                violations.append(record)

                break

    return violations


# ============================================================
# ПОПРОШАЙНИЧЕСТВО
# ============================================================

def analyze_begging_frequency():

    messages = load_messages()

    by_user = {}

    for msg in messages:

        if msg["text"]:

            if find_patterns(
                msg["text"].lower(),
                BEGGING_PATTERNS
            ):

                by_user.setdefault(
                    msg["user_id"],
                    []
                ).append(msg)

    found = []

    for user_id, msgs in by_user.items():

        msgs.sort(
            key=lambda x: x["date"]
        )

        for i in range(len(msgs)):

            try:

                start = datetime.strptime(
                    msgs[i]["date"],
                    "%Y-%m-%d %H:%M:%S"
                )

            except Exception:
                continue

            count = 0

            for msg in msgs[i:]:

                try:

                    t = datetime.strptime(
                        msg["date"],
                        "%Y-%m-%d %H:%M:%S"
                    )

                except Exception:
                    continue

                if (
                    t - start
                    <= timedelta(minutes=10)
                ):

                    count += 1

                else:
                    break

            if count > 3:

                violation = {
                    "rule": "1.7",
                    "reason":
                        f"Попрошайничество более "
                        f"3 раз за 10 минут "
                        f"({count} сообщений)."
                }

                record = save_violation(
                    msgs[i],
                    violation
                )

                notify_admin(
                    msgs[i],
                    violation
                )

                found.append(record)

                break

    return found


# ============================================================
# СТАТИСТИКА
# ============================================================

def get_statistics():

    messages = load_messages()

    violations = load_violations()

    rule_counter = Counter(
        v["rule"]
        for v in violations
    )

    user_counter = Counter(
        v["display_name"]
        for v in violations
    )

    return (
        messages,
        violations,
        rule_counter,
        user_counter
    )


# ============================================================
# /START
# ============================================================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    bot.reply_to(
        message,

        "👋 <b>Бот-анализатор чатов</b>\n\n"

        "Я сохраняю сообщения и проверяю "
        "их на нарушения правил.\n\n"

        "<b>Команды:</b>\n"
        "/report — полный отчёт\n"
        "/violations — последние нарушения\n"
        "/stats — статистика\n"
        "/clear — удалить данные\n"
        "/scan — повторно проверить сообщения\n"
        "/id — показать ID\n\n"

        "При обнаружении нарушения "
        "администратору автоматически "
        "отправляется уведомление."
    )


# ============================================================
# /ID
# ============================================================

@bot.message_handler(
    commands=["id"]
)
def id_command(message):

    bot.reply_to(
        message,

        f"🆔 <b>ID чата:</b> "
        f"<code>{message.chat.id}</code>\n"

        f"👤 <b>Твой ID:</b> "
        f"<code>{message.from_user.id}</code>"
    )


# ============================================================
# ОБРАБОТКА СООБЩЕНИЙ
# ============================================================

@bot.message_handler(
    content_types=[
        "text",
        "photo",
        "video",
        "document",
        "sticker",
        "animation",
        "audio",
        "voice"
    ]
)
def all_messages(message):

    if (
        message.text
        and message.text.startswith("/")
    ):
        return

    data, violations = process_message(
        message
    )

    print("=" * 60)

    print(
        "Новое сообщение"
    )

    print(
        "Пользователь:",
        data["display_name"]
    )

    print(
        "Дата:",
        data["date"]
    )

    print(
        "Текст:",
        data["text"]
    )

    if violations:

        print(
            "!!! НАЙДЕНЫ НАРУШЕНИЯ !!!"
        )

        for v in violations:

            print(
                v["rule"],
                "-",
                v["rule_name"],
                "-",
                v["reason"]
            )

    print("=" * 60)


# ============================================================
# /SCAN
# ============================================================

@bot.message_handler(
    commands=["scan"]
)
def scan_command(message):

    if not is_admin(message):
        return

    bot.reply_to(
        message,
        "🔎 Начинаю повторный анализ..."
    )

    messages = load_messages()

    count = 0

    for data in messages:

        found = analyze_message(
            data.get("text", "")
        )

        for violation in found:

            save_violation(
                data,
                violation
            )

            notify_admin(
                data,
                violation
            )

            count += 1

    spam = analyze_spam()

    begging = analyze_begging_frequency()

    count += len(spam)
    count += len(begging)

    bot.reply_to(
        message,

        f"✅ Анализ завершён.\n\n"
        f"Сообщений проверено: "
        f"<b>{len(messages)}</b>\n"
        f"Нарушений найдено: "
        f"<b>{count}</b>"
    )


# ============================================================
# /STATS
# ============================================================

@bot.message_handler(
    commands=["stats"]
)
def stats_command(message):

    if not is_admin(message):
        return

    (
        messages,
        violations,
        rule_counter,
        user_counter
    ) = get_statistics()

    text = (
        "📊 <b>Статистика</b>\n\n"

        f"💬 Сообщений: "
        f"<b>{len(messages)}</b>\n"

        f"⚠️ Нарушений: "
        f"<b>{len(violations)}</b>\n\n"
    )

    if rule_counter:

        text += "<b>По правилам:</b>\n"

        for rule, count in (
            rule_counter.most_common()
        ):

            text += (
                f"• {rule} — "
                f"{RULES[rule]['name']}: "
                f"<b>{count}</b>\n"
            )

    text += "\n<b>Нарушители:</b>\n"

    for user, count in (
        user_counter.most_common(10)
    ):

        text += (
            f"• {user} — "
            f"<b>{count}</b>\n"
        )

    bot.reply_to(
        message,
        text
    )


# ============================================================
# /VIOLATIONS
# ============================================================

@bot.message_handler(
    commands=["violations"]
)
def violations_command(message):

    if not is_admin(message):
        return

    violations = load_violations()

    if not violations:

        bot.reply_to(
            message,
            "✅ Нарушений пока не найдено."
        )

        return

    last = violations[-15:]

    text = (
        "⚠️ <b>Последние нарушения</b>\n\n"
    )

    for v in reversed(last):

        username = (
            "@"
            + v["username"]
            if v["username"]
            else v["display_name"]
        )

        text += (
            f"🔴 <b>{v['rule']}</b> — "
            f"{v['rule_name']}\n"

            f"👤 {username}\n"

            f"🕐 {v['date']}\n"

            f"💬 {v['text'][:250]}\n"

            f"📌 {v['reason']}\n"
        )

        if v.get("link"):

            text += (
                f'🔗 <a href="{v["link"]}">'
                "Сообщение</a>\n"
            )

        text += "\n"

    bot.send_message(
        message.chat.id,
        text,
        disable_web_page_preview=True
    )


# ============================================================
# /REPORT
# ============================================================

@bot.message_handler(
    commands=["report"]
)
def report_command(message):

    if not is_admin(message):
        return

    (
        messages,
        violations,
        rule_counter,
        user_counter
    ) = get_statistics()

    if not violations:

        bot.reply_to(
            message,
            "📊 Отчёт пуст — "
            "нарушений не найдено."
        )

        return

    text = (
        "📊 <b>ОТЧЁТ ПО ЧАТУ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"💬 Всего сообщений: "
        f"<b>{len(messages)}</b>\n"

        f"⚠️ Всего нарушений: "
        f"<b>{len(violations)}</b>\n\n"
    )

    text += (
        "<b>Нарушения по правилам:</b>\n"
    )

    for rule, count in (
        rule_counter.most_common()
    ):

        text += (
            f"• <b>{rule}</b> "
            f"{RULES[rule]['name']} — "
            f"{count}\n"
        )

    text += "\n<b>Топ нарушителей:</b>\n"

    for user, count in (
        user_counter.most_common(10)
    ):

        text += (
            f"• {user} — {count}\n"
        )

    text += (
        "\n━━━━━━━━━━━━━━━━━━\n"
        "Подробности: /violations"
    )

    bot.reply_to(
        message,
        text
    )


# ============================================================
# /CLEAR
# ============================================================

@bot.message_handler(
    commands=["clear"]
)
def clear_command(message):

    if not is_admin(message):
        return

    save_json(
        MESSAGES_FILE,
        []
    )

    save_json(
        VIOLATIONS_FILE,
        []
    )

    bot.reply_to(
        message,
        "🗑 Все сохранённые "
        "сообщения и нарушения удалены."
    )


# ============================================================
# ЗАПУСК
# ============================================================

print(
    "🤖 Бот-анализатор запущен!"
)

print(
    "📁 Сообщения:",
    MESSAGES_FILE
)

print(
    "⚠️ Нарушения:",
    VIOLATIONS_FILE
)

print(
    "📨 Уведомления отправляются "
    "на ID: 8780322706"
)

print(
    "Ожидаю сообщения..."
)

bot.infinity_polling(
    skip_pending=True,
    timeout=60,
    long_polling_timeout=60
)
