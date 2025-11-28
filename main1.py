# main.py
import os
import telebot
import pkgutil
import importlib

TELEGRAM_TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(
    TELEGRAM_TOKEN,
    parse_mode="HTML",
    skip_pending=True
)

def auto_register_handlers():
    package = "bot"

    for _, module_name, _ in pkgutil.iter_modules([package]):
        full_name = f"{package}.{module_name}"
        module = importlib.import_module(full_name)

        # Tự tìm hàm bắt đầu bằng "register_"
        for attr in dir(module):
            if attr.startswith("register_"):
                func = getattr(module, attr)
                if callable(func):
                    func(bot)
                    print(f"Loaded: {attr} from {module_name}")

auto_register_handlers()

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
