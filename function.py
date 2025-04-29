import sqlite3
import random
from responses import join_responses, pidor_responses, krasavchik_responses
from datetime import datetime

DB_NAME = "chat_family.db"


# Функции для случайного выбора фраз
def get_random_phrase(phrases_list, username, telegram_id):
    # Фильтруем фразы в зависимости от наличия {name} или {tg}
    if username or telegram_id:  # Если передано имя или тег
        matching_phrases = [phrase for phrase in phrases_list if '{name}' in phrase or '{tg}' in phrase]
    else:  # Если нет имени и тега, выбираем фразы без них
        matching_phrases = [phrase for phrase in phrases_list if '{name}' not in phrase and '{tg}' not in phrase]

    if not matching_phrases:
        return "Не найдена подходящая фраза."

    # Выбираем случайную фразу
    chosen_phrase = random.choice(matching_phrases)

    # Если в фразе есть шаблон {name}, заменяем его на имя
    if '{name}' in chosen_phrase:
        chosen_phrase = chosen_phrase.replace('{name}', username)

    # Если в фразе есть шаблон {tg}, заменяем его на тег
    if '{tg}' in chosen_phrase:
        chosen_phrase = chosen_phrase.replace('{tg}', '@' + telegram_id)

    return chosen_phrase


def initialize_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            language_code TEXT,
            chat_id INTEGER
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS winners (
            date TEXT PRIMARY KEY,
            pidor_id INTEGER,
            krasavchik_id INTEGER
        )
        """)
        conn.commit()


def join_raffle(user_id, username, first_name, last_name, full_name, language_code, chat_id):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM participants WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
        if c.fetchone():
            return "Ты ебанутый?\nЧто ты тут тыкаешь??"

        c.execute("""
            INSERT INTO participants (user_id, username, first_name, last_name, full_name, language_code, chat_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, first_name, last_name, full_name, language_code, chat_id))
        conn.commit()
        return get_random_phrase(phrases_list=join_responses, username=first_name, telegram_id=username)


def choose_pidor():
    today = datetime.now().date().isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()

        # Проверяем, был ли уже выбран победитель Пидор дня
        c.execute("SELECT * FROM winners WHERE date = ?", (today,))
        row = c.fetchone()

        if row and row[1]:  # Если Пидор дня уже есть
            c.execute("SELECT username, first_name FROM participants WHERE user_id = ?", (row[1],))
            user_data = c.fetchone()
            return get_random_phrase(phrases_list=pidor_responses, telegram_id=user_data[0], username=user_data[1])

        # Если нет победителей, выбираем случайного пользователя
        c.execute("SELECT user_id, username, first_name FROM participants")
        users = c.fetchall()

        if not users:
            return "Одни сыкуны похоже 😢 ..."

        # Выбираем случайного пользователя
        pidor_data = random.choice(users)
        pidor_id, pidor_username, pidor_first_name = pidor_data

        # Записываем в базу, кто стал Пидором дня
        c.execute("INSERT OR REPLACE INTO winners (date, pidor_id) VALUES (?, ?)", (today, pidor_id))

        # Возвращаем случайную фразу с именем и никнеймом
        return get_random_phrase(phrases_list=pidor_responses, telegram_id=pidor_username, username=pidor_first_name)


def choose_krasavchik():
    today = datetime.now().date().isoformat()
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM winners WHERE date = ?", (today,))
        row = c.fetchone()
        if row and row[2]:
            c.execute("SELECT username FROM participants WHERE user_id = ?", (row[2],))
            return c.fetchone()[0]
        c.execute("SELECT user_id FROM participants")
        users = [r[0] for r in c.fetchall()]
        if not users:
            return "одни сыкуны похоже 😢 ..."
        pidor_id = row[1] if row else None
        filtered = [u for u in users if u != pidor_id]
        if not filtered:
            return "Хватит с тебя чинов PI-дор комнатный"
        krasavchik_id = random.choice(filtered)
        if row:
            c.execute("UPDATE winners SET krasavchik_id = ? WHERE date = ?", (krasavchik_id, today))
        else:
            c.execute("INSERT INTO winners (date, krasavchik_id) VALUES (?, ?)", (today, krasavchik_id))
        c.execute("SELECT username FROM participants WHERE user_id = ?", (krasavchik_id,))
        return get_random_phrase(phrases_list=krasavchik_responses, username='', telegram_id=c.fetchone()[0])
