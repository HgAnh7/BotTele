import os
import sys
import importlib.util
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

MODULE_DIR = os.path.join(os.path.dirname(__file__), "bot")

def load_modules():
    for fn in os.listdir(MODULE_DIR):
        if fn.endswith(".py") and not fn.startswith("_"):
            path = os.path.join(MODULE_DIR, fn)
            try:
                spec = importlib.util.spec_from_file_location(fn[:-3], path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "register") and callable(mod.register):
                    mod.register(bot)
                    print(f"[OK] Loaded {fn}")
                else:
                    print(f"[FAIL] {fn} không có register(bot)")
            except Exception as e:
                print(f"[ERROR] Lỗi khi load {fn}: {e}")

if __name__ == "__main__":
    load_modules()
    print("Bot đang chạy...")
    bot.infinity_polling()
