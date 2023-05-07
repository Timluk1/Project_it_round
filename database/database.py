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

    async def add_server_hardware(self, state, count):
        async with state.proxy() as data:
            # Добавляем запись о новом пользователе в таблицу users
            self.cur.execute(
                "INSERT INTO users (id, model, year_of_release) VALUES (?, ?, ?)",
                (data["user_id"], data['model'], data['year_of_release']))

            # Добавляем запись об оборудовании в таблицу models
            self.cur.execute(
                "INSERT INTO models (id, model, manufacturer, energy_cost, additional_expenses, date, count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (data["user_id"], data['model'], data["manufacturer"], data['energy_cos'], data['additional_expenses'],
                 dt.datetime.now().date(),
                 count))

            self.base.commit()

    async def server_hardware_in_db(self, state):
        async with state.proxy() as data:
            # Проверяем наличие товара с заданным именем
            self.cur.execute("SELECT COUNT(*) FROM models WHERE model=? AND id=? AND manufacturer=?",
                             (data["model"], data["user_id"], data["manufacturer"]))
            result = self.cur.fetchone()[0]

        if result > 0:
            return True
        return False

    async def add_quantity(self, state):
        async with state.proxy() as data:
            # Увеличиваем количество оборудования в таблице models на 1
            self.cur.execute("UPDATE models SET count = count + 1 WHERE model=? and id=? AND manufacturer=?",
                             (data["model"], data["user_id"], data["manufacturer"]))
            self.base.commit()

    async def expense_data_sql(self, user_id):
        return self.cur.execute(
            "SELECT model, manufacturer, energy_cost, additional_expenses, count, date, (energy_cost * count) + (additional_expenses * count) FROM models WHERE id=?",
            (user_id,)).fetchall()

    async def delete_model_sql(self, state):
        async with state.proxy() as data:
            data_db = self.cur.execute("SELECT id FROM models WHERE id=? AND model=? AND manufacturer=?",
                             (data["delete_user_id"], data["delete_model"], data["delete_manufacturer"])).fetchall()
            if len(data_db) == 0:
                return None
            else:
                self.cur.execute("DELETE FROM users WHERE id=? AND model=?", (data["delete_user_id"], data["delete_model"]))
                self.cur.execute("DELETE FROM models WHERE id=? AND model=? AND manufacturer=?", (data["delete_user_id"], data["delete_model"], data["delete_manufacturer"]))
                self.base.commit()
                return True

    async def get_minimum_amount(self, user_id):
        return self.cur.execute(
            "SELECT model, manufacturer, energy_cost, additional_expenses, count, (energy_cost * count) + (additional_expenses * count) FROM models WHERE id=? ORDER BY (additional_expenses + energy_cost) LIMIT 1;",
            (user_id,)).fetchall()[0]
