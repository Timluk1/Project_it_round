from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, Dispatcher, StatesGroup
from aiogram import types
from aiogram.utils import executor
from database import Database
import datetime as dt
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text


class FSM_equipmen(StatesGroup):
    '''Класс состояний для получения модели оборудования'''
    model = State()
    manufacturer = State()
    year_of_release = State()
    energy_cos = State()
    additional_expenses = State()


class FSM_delete_model(StatesGroup):
    '''Класс состояний для удаления оборудования из бд'''
    delete_model = State()
    delete_manufacturer = State()


class Client:
    def __init__(self, token):
        self.storage = MemoryStorage()

        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=self.storage)

        # Кнопка отмены для выхода из состояний
        self.kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        self.kb.add(KeyboardButton("Отмена"))

        # Кнопки для основного меню
        self.menu = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        self.menu.add(KeyboardButton("Добавить оборудование ⚙️"))
        self.menu.add(KeyboardButton("Помощь 🆘"))
        self.menu.add(KeyboardButton("Расходы 💵"))
        self.menu.add(KeyboardButton("Удалить модель ❌"))
        self.menu.add(KeyboardButton("Выгодная модель 🏷️"))

        # Подключение к базе данных
        self.database = Database()
        self.database.start()

    async def start(self, message: types.Message):
        '''Стартовый вывод'''
        await self.bot.send_message(message.from_user.id,
                                    "Добро пожаловать в чат бота для расчета стоимости и эксплуатации серверного оборудования.\n"
                                    "\nКоманды бота:\n\n"
                                    "Помощь: \n /help\n\n"
                                    "Добавить новое оборудование: \n/add_equipment\n\n"
                                    "Узнать данные о расходах на оборудование: \n/expense_data\n\n"
                                    "Удалить модель: \n/delete_model\n\n"
                                    "Самая выгодная модель: \n/minimum_amount", reply_markup=self.menu)

    async def client(self, message: types.Message):
        '''Обработчик текстовых команд'''
        if "Добавить оборудование ⚙️" in message.text:
            await FSM_equipmen.model.set()
            await self.bot.send_message(message.from_user.id, "Введите название модели", reply_markup=self.kb)

        elif "Помощь 🆘" in message.text:
            await self.bot.send_message(message.from_user.id,
                                        "\nКоманды бота:\n\n"
                                        "Помощь: \n/help\n\n"
                                        "Добавить новое оборудование: \n/add_equipment\n\n"
                                        "Узнать данные о расходах на оборудование: \n/expense_data\n\n"
                                        "Удалить модель: \n/delete_model\n\n"
                                        "Самая выгодная модель: \n/minimum_amount", reply_markup=self.menu)

        elif "Расходы 💵" in message.text:
            if "Добавить оборудование" in message.text:
                await FSM_equipmen.model.set()
                await self.bot.send_message(message.from_user.id, "Введите название модели", reply_markup=self.kb)
            elif "Помощь" in message.text:
                pass
            elif "Расходы":
                expenses = self.database.expense_data_sql(message.from_user.id)
                if len(expenses) == 0:
                    await self.bot.send_message(message.from_user.id,
                                                "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
                else:
                    sm = 0
                    for expense in expenses:
                        await self.bot.send_message(message.from_user.id, f"Название модели: \n{expense[0]}.\n\n"
                                                                          f"Производитель модели: \n{expense[1]}.\n\n"
                                                                          f"Расходы на электроэнергию: \n{expense[2]} Р.\n\n"
                                                                          f"Дополнительные расходы: \n{expense[3]} Р.\n\n"
                                                                          f"Количество: \n{expense[4]} шт.\n\n"
                                                                          f"Суммарная трата на данную модель: \n{round(expense[6], 2)}. Р")
                        sm += expense[6]
                    await self.bot.send_message(message.from_user.id,
                                                f"Суммарная трата на все оборудование: \n{round(sm, 2)}")
        elif "Удалить модель ❌" in message.text:
            expenses = self.database.expense_data_sql(message.from_user.id)
            if len(expenses) == 0:
                await self.bot.send_message(message.from_user.id,
                                            "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
            else:
                await FSM_delete_model.delete_model.set()
                await self.bot.send_message(message.from_user.id, "Введите название модели", reply_markup=self.kb)

        elif "Выгодная модель 🏷️" in message.text:
            expenses = self.database.expense_data_sql(message.from_user.id)
            if len(expenses) == 0:
                await self.bot.send_message(message.from_user.id,
                                            "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
            else:
                mn = self.database.get_minimum_amount(message.from_user.id)
                await self.bot.send_message(message.from_user.id, f"Самое выгодное серверное оборудование:\n"
                                                                  f"Название модели: \n{mn[0]}.\n\n"
                                                                  f"Производитель модели: \n{mn[1]}.\n\n"
                                                                  f"Расходы на электроэнергию: \n{mn[2]} Р.\n\n"
                                                                  f"Дополнительные расходы: \n{mn[3]} Р.\n\n"
                                                                  f"Количество: \n{mn[4]} шт.\n\n"
                                                                  f"Суммарная трата на данную модель: \n{round(mn[5], 2)}. Р")
        else:
            await self.bot.send_message(message.from_user.id,
                                        "Нет такой команды, воспользуйтесь командой /help, чтобы увидеть список команд.")

    async def add_equipment_start(self, message: types.Message):
        await FSM_equipmen.model.set()
        await self.bot.send_message(message.from_user.id, "Введите название модели", reply_markup=self.kb)

    async def exit(self, message: types.Message, state: FSMContext):
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await self.bot.send_message(message.from_user.id, "Ок", reply_markup=self.menu)

    async def add_model(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['model'] = message.text

        await self.bot.send_message(message.from_user.id, "Введите производителя", reply_markup=self.kb)
        await FSM_equipmen.next()

    async def add_manufacturer(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['manufacturer'] = message.text

        await self.bot.send_message(message.from_user.id, "Введите год выпуска в формате ДД.ММ.ГГГГ",
                                    reply_markup=self.kb)
        await FSM_equipmen.next()

    async def add_year_of_release(self, message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                date = message.text.split(".")
                date = dt.date(int(date[2]), int(date[1]), int(date[0]))
                data['year_of_release'] = date
            await self.bot.send_message(message.from_user.id, "Введите данные о расходах на электроэнергию в месяц",
                                        reply_markup=self.kb)
            await FSM_equipmen.next()
        except Exception:
            await self.bot.send_message(message.from_user.id, "Некорректный год выпуска! Попробуйте еще раз\n"
                                                              "Год выпуска должен быть в формате ДД.ММ.ГГГГ",
                                        reply_markup=self.kb)

    async def add_energy_cos(self, message: types.Message, state: FSMContext):
        try:
            async with state.proxy() as data:
                data['energy_cos'] = float(message.text)
            await self.bot.send_message(message.from_user.id, "Введите данные о дополнительных расходах",
                                        reply_markup=self.kb)
            await FSM_equipmen.next()
        except Exception:
            await self.bot.send_message(message.from_user.id,
                                        "Пожалуйста попробуйте еще раз и введите число с плавающей точкой или обычное число, например (1.21)",
                                        reply_markup=self.kb)

    async def additional_expenses(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['additional_expenses'] = float(message.text)
        if self.database.server_hardware_in_db(data["model"], message.from_user.id):
            self.database.add_quantity(data["model"], message.from_user.id, data["manufacturer"])
            await self.bot.send_message(message.from_user.id, "Данные успешно добавлены в БД", reply_markup=self.menu)
        else:
            self.database.add_server_hardware(data, message.from_user.id, 1)
            await self.bot.send_message(message.from_user.id, "Данные успешно добавлены в БД", reply_markup=self.menu)

            # Завершаем процесс добавления оборудования
        await state.finish()

    async def expense_data(self, message: types.Message):
        expenses = self.database.expense_data_sql(message.from_user.id)
        if len(expenses) == 0:
            await self.bot.send_message(message.from_user.id,
                                        "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
        else:
            sm = 0
            for expense in expenses:
                await self.bot.send_message(message.from_user.id, f"Название модели: \n{expense[0]}.\n\n"
                                                                  f"Производитель модели: \n{expense[1]}.\n\n"
                                                                  f"Расходы на электроэнергию: \n{expense[2]} Р.\n\n"
                                                                  f"Дополнительные расходы: \n{expense[3]} Р.\n\n"
                                                                  f"Количество: \n{expense[4]} шт.\n\n"
                                                                  f"Суммарная трата на данную модель: \n{round(expense[6], 2)}. Р")
                sm += expense[6]
            await self.bot.send_message(message.from_user.id,
                                        f"Суммарная трата на все оборудование \n{round(sm, 2)}")

    async def delete_model_start(self, message: types.Message):
        expenses = self.database.expense_data_sql(message.from_user.id)
        if len(expenses) == 0:
            await self.bot.send_message(message.from_user.id,
                                        "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
        else:
            await FSM_delete_model.delete_model.set()
            await self.bot.send_message(message.from_user.id, "Введите название модели", reply_markup=self.kb)

    async def delete_model(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['delete_model'] = message.text
        await self.bot.send_message(message.from_user.id, "Введите название производителя модели", reply_markup=self.kb)
        await FSM_delete_model.next()

    async def delete_model_manufacturer(self, message: types.Message, state: FSMContext):
        async with state.proxy() as data:
            data['delete_manufacturer'] = message.text
        try:
            self.database.delete_model_sql(message.from_user.id, data["delete_model"], data["delete_manufacturer"])
            await self.bot.send_message(message.from_user.id,
                                        f"Модель {data['delete_model']} от производителя {data['delete_manufacturer']} уcпешно удалена!",
                                        reply_markup=self.menu)
            await state.finish()
        except Exception:
            await self.bot.send_message(message.from_user.id, "Возможно вы не добавляли модель и она не удалилась.\n"
                                                              "Используйте команду: /expense_date, чтобы посмотреть ваши добавленные модели сервеного оборудования",
                                        reply_markup=self.menu)
            await state.finish()

    async def minimum_amount_user(self, message: types.Message):
        expenses = self.database.expense_data_sql(message.from_user.id)
        if len(expenses) == 0:
            await self.bot.send_message(message.from_user.id,
                                        "У вас еще нет добавленых моделей сервеного оборудования.\nИспользуйте команду /add_equipment, чтобы добавить оборудование.")
        else:
            mn = self.database.get_minimum_amount(message.from_user.id)
            await self.bot.send_message(message.from_user.id, f"Самое выгодное серверное оборудование:\n\n"
                                                              f"Название модели: \n{mn[0]}.\n\n"
                                                              f"Производитель модели: \n{mn[1]}.\n\n"
                                                              f"Расходы на электроэнергию: \n{mn[2]} Р.\n\n"
                                                              f"Дополнительные расходы: \n{mn[3]} Р.\n\n"
                                                              f"Количество: \n{mn[4]} шт.\n\n"
                                                              f"Суммарная трата на данную модель: \n{round(mn[5], 2)}. Р")

    async def help(self, message: types.Message):
        await self.bot.send_message(message.from_user.id,
                                    "\nКоманды бота:\n\n"
                                    "Помощь: \n/help\n\n"
                                    "Добавить новое оборудование: \n/add_equipment\n\n"
                                    "Узнать данные о расходах на оборудование: \n/expense_data\n\n"
                                    "Удалить модель: \n/delete_model\n\n"
                                    "Самая выгодная модель: \n/minimum_amount", reply_markup=self.menu)

    def register_admin_handlers(self, dp: Dispatcher):
        '''Регестрируем все хэндлеры'''
        dp.register_message_handler(self.start, commands=["start"])
        dp.register_message_handler(self.exit, state="*", commands='отмена')
        dp.register_message_handler(self.exit, Text(equals="отмена", ignore_case=True), state="*")
        dp.register_message_handler(self.add_equipment_start, commands=["add_equipment"], state=None)
        dp.register_message_handler(self.expense_data, commands=["expense_data"], state=None)
        dp.register_message_handler(self.add_model, state=FSM_equipmen.model)
        dp.register_message_handler(self.add_manufacturer, state=FSM_equipmen.manufacturer)
        dp.register_message_handler(self.add_year_of_release, state=FSM_equipmen.year_of_release)
        dp.register_message_handler(self.add_energy_cos, state=FSM_equipmen.energy_cos)
        dp.register_message_handler(self.additional_expenses, state=FSM_equipmen.additional_expenses)
        dp.register_message_handler(self.delete_model_start, commands=["delete_model"], state=None)
        dp.register_message_handler(self.delete_model, state=FSM_delete_model.delete_model)
        dp.register_message_handler(self.delete_model_manufacturer, state=FSM_delete_model.delete_manufacturer)
        dp.register_message_handler(self.minimum_amount_user, commands=["minimum_amount"])
        dp.register_message_handler(self.help, commands=["help"])
        dp.register_message_handler(self.client)


if __name__ == "__main__":
    client = Client("token")
    client.register_admin_handlers(client.dp)
    executor.start_polling(client.dp, skip_updates=True)
