from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, Dispatcher, StatesGroup
from aiogram import types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from database import Database
import datetime as dt
import os


class FSM_equipmen(StatesGroup):
    model = State()
    manufacturer = State()
    year_of_release = State()
    energy_cos = State()
    additional_expenses = State()


class Client:
    def __init__(self, token):
        self.storage = MemoryStorage()

        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=self.storage)
        self.database = Database()
        self.database.start()

    async def start(self, message: types.Message):
        await self.bot.send_message(message.from_user.id,
                                    "Добро пожаловать в чат бота для расчета стоимости и эксплуатации серверного оборудования.\n"
                                    "\nВозможности бота:\n"
                                    "Добавить новое оборудование: /add_equipment")

    async def add_equipment_start(self, message: types.Message):
        await FSM_equipmen.model.set()
        await self.bot.send_message(message.from_user.id, "Введите название модели")

    async def add_model(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['model'] = message.text

        await self.bot.send_message(message.from_user.id, "Введите производителя")
        await FSM_equipmen.next()

    async def add_manufacturer(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['manufacturer'] = message.text

        await self.bot.send_message(message.from_user.id, "Введите год выпуска в формате ДД.ММ.ГГГГ")
        await FSM_equipmen.next()

    async def add_year_of_release(self, message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                date = message.text.split(".")
                date = dt.date(int(date[2]), int(date[1]), int(date[0]))
                data['year_of_release'] = date
            await self.bot.send_message(message.from_user.id, "Введите данные о расходах на электроэнергию в месяц")
            await FSM_equipmen.next()
        except Exception:
            await self.bot.send_message(message.from_user.id, "Некорректный год выпуска! Попробуйте еще раз\n"
                                                              "Год выпуска должен быть в формате ДД.ММ.ГГГГ")

    async def add_energy_cos(self, message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['energy_cos'] = float(message.text)
            await self.bot.send_message(message.from_user.id, "Введите данные о дополнительных расходах")
            await FSM_equipmen.next()
        except Exception:
            await self.bot.send_message(message.from_user.id,
                                        "Пожалуйста попробуйте еще раз и введите число с плавающей точкой или обычное число, например (1.21)")

    async def additional_expenses(self, message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['additional_expenses'] = float(message.text)
            if self.database.server_hardware_in_db(data["model"], message.from_user.id):
                self.database.add_quantity(data["model"], message.from_user.id)
                await self.bot.send_message(message.from_user.id, "Данные успешно добавлены в БД")
            else:
                self.database.add_server_hardware(data, message.from_user.id, 1)
                await self.bot.send_message(message.from_user.id, "Данные успешно добавлены в БД")

            # Завершаем процесс добавления оборудования
            await state.finish()

        except Exception:
            await self.bot.send_message(message.from_user.id,
                                        "Пожалуйста попробуйте еще раз и введите число с плавающей точкой или обычное число, например (1.21)")

    def register_admin_handlers(self, dp: Dispatcher):
        dp.register_message_handler(self.start, commands=["start"])
        dp.register_message_handler(self.add_equipment_start, commands=["add_equipment"], state=None)
        dp.register_message_handler(self.add_model, state=FSM_equipmen.model)
        dp.register_message_handler(self.add_manufacturer, state=FSM_equipmen.manufacturer)
        dp.register_message_handler(self.add_year_of_release, state=FSM_equipmen.year_of_release)
        dp.register_message_handler(self.add_energy_cos, state=FSM_equipmen.energy_cos)
        dp.register_message_handler(self.additional_expenses, state=FSM_equipmen.additional_expenses)


if __name__ == "__main__":
    client = Client("5762130910:AAGmI6Alyh8_6OkqvoX7b1i1TZKCM3ICPas")
    client.register_admin_handlers(client.dp)
    executor.start_polling(client.dp, skip_updates=True)
