import sqlite3


def create_table(api_key, language):
    sqlite_connection = sqlite3.connect("user_settings.db")
    cursor = sqlite_connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS settings
                    (id INTEGER,
                    api_key TEXT,
                    language TEXT)""")
    values = (1, api_key, language)
    cursor.execute("""INSERT INTO settings (id, api_key, language) VALUES (?, ?, ?)""", values)
    sqlite_connection.commit()
    sqlite_connection.close()


def get_settings():
    sqlite_connection = sqlite3.connect("user_settings.db")
    cursor = sqlite_connection.cursor()
    cursor.execute("SELECT api_key, language FROM settings")
    settings = cursor.fetchall()
    sqlite_connection.commit()
    sqlite_connection.close()
    return settings


def settings_ex():
    sqlite_connection = sqlite3.connect("user_settings.db")
    cursor = sqlite_connection.cursor()
    cursor.execute("""SELECT count(name) FROM sqlite_master WHERE type='table' AND name='settings'""")
    set_ex = cursor.fetchone()[0]
    sqlite_connection.commit()
    sqlite_connection.close()
    return set_ex


def update_lung(lung):
    sqlite_connection = sqlite3.connect("user_settings.db")
    cursor = sqlite_connection.cursor()
    cursor.execute("""UPDATE settings SET language=? WHERE id=?""", (lung, 1))
    sqlite_connection.commit()
    sqlite_connection.close()


def delete_table():
    sqlite_connection = sqlite3.connect("user_settings.db")
    cursor = sqlite_connection.cursor()
    cursor.execute("""DROP TABLE IF EXISTS settings""")
    sqlite_connection.commit()
    sqlite_connection.close()