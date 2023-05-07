from handlers.client import Client
from aiogram.utils import executor


client = Client("5762130910:AAGmI6Alyh8_6OkqvoX7b1i1TZKCM3ICPas")
client.register_admin_handlers(client.dp)
executor.start_polling(client.dp, skip_updates=True)