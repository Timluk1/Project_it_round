from handlers.client import Client
from aiogram.utils import executor


client = Client("TOKEN")
client.register_admin_handlers(client.dp)
executor.start_polling(client.dp, skip_updates=True)
