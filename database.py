import sqlite3 as sq
import datetime


class Database:
    def __init__(self):
        self.base = sq.connect("res.db")
        self.cur = self.base.cursor()

    def start(self):
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS users (id TEXT, model TEXT, manufacturer TEXT, year_of_release TEXT)")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS models (id TEXT, model TEXT, energy_cost REAL, additional_expenses REAL, count INTEGER, date TEXT)")

    def add_server_hardware(self, data, user_id, count):
        self.cur.execute(
            "INSERT INTO users (id, model, manufacturer, year_of_release) VALUES (?, ?, ?, ?)",
            (user_id, data['model'], data['manufacturer'], data['year_of_release']))

        self.cur.execute(
            "INSERT INTO models (id, model, energy_cost, additional_expenses, date, count) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, data['model'], data['energy_cos'], data['additional_expenses'], datetime.datetime.now().date(), count))

        self.base.commit()

    def server_hardware_in_db(self, name, user_id):
        # Проверяем наличие товара с заданным именем
        self.cur.execute("SELECT COUNT(*) FROM models WHERE model=? AND id=?", (name, user_id))
        result = self.cur.fetchone()[0]

        if result > 0:
            return True
        return False

    def add_quantity(self, name, user_id):
        self.cur.execute("UPDATE models SET count = count + 1 WHERE model = ? and id = ?", (name, user_id))
        self.base.commit()


