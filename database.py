import sqlite3 as sq
import datetime as dt


class Database:
    def __init__(self):
        # Устанавливаем соединение с базой данных res.db
        self.base = sq.connect("server_hardware.db")
        self.cur = self.base.cursor()

    def start(self):
        # Создаем таблицу users для хранения информации о пользователях и их добавленной модели и ее года выпуска
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS users (id TEXT, model TEXT, year_of_release TEXT)")

        # Создаем таблицу models для хранения информации об оборудовании
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS models (id TEXT, model TEXT, manufacturer TEXT, energy_cost REAL, additional_expenses REAL, count INTEGER, date TEXT)")

    def add_server_hardware(self, data, user_id, count):
        # Добавляем запись о новом пользователе в таблицу users
        self.cur.execute(
            "INSERT INTO users (id, model, year_of_release) VALUES (?, ?, ?)",
            (user_id, data['model'], data['year_of_release']))

        # Добавляем запись об оборудовании в таблицу models
        self.cur.execute(
            "INSERT INTO models (id, model, manufacturer, energy_cost, additional_expenses, date, count) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, data['model'], data["manufacturer"], data['energy_cos'], data['additional_expenses'],
             dt.datetime.now().date(),
             count))

        self.base.commit()

    def server_hardware_in_db(self, name, user_id):
        # Проверяем наличие товара с заданным именем
        self.cur.execute("SELECT COUNT(*) FROM users WHERE model=? AND id=?",
                         (name, user_id))
        result = self.cur.fetchone()[0]

        if result > 0:
            return True
        return False

    def add_quantity(self, name, user_id, manufacturer):
        # Увеличиваем количество оборудования в таблице models на 1
        self.cur.execute("UPDATE models SET count = count + 1 WHERE model=? and id=? AND manufacturer=?",
                         (name, user_id, manufacturer))
        self.base.commit()

    def expense_data_sql(self, user_id):
        return self.cur.execute(
            "SELECT model, manufacturer, energy_cost, additional_expenses, count, date, (energy_cost * count) + (additional_expenses * count) FROM models WHERE id=?",
            (user_id,)).fetchall()

    def delete_model_sql(self, user_id, name, manufacturer):
        self.cur.execute("DELETE FROM users WHERE id=? AND model=?", (user_id, name))
        self.cur.execute("DELETE FROM models WHERE id=? AND model=? AND manufacturer=?", (user_id, name, manufacturer))
        self.base.commit()

    def get_minimum_amount(self, user_id):
        return self.cur.execute(
            "SELECT model, manufacturer, energy_cost, additional_expenses, count, (energy_cost * count) + (additional_expenses * count) FROM models WHERE id=? ORDER BY (additional_expenses + energy_cost) LIMIT 1;",
            (user_id,)).fetchall()[0]
