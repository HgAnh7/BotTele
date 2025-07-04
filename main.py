# main.py
import os
import telebot
from bot.nct import register_nct
from bot.scl import register_scl
from bot.in4 import register_in4
from bot.send import register_send
from bot.time import register_time
from bot.help import register_help
from bot.thumb import register_thumb
from bot.proxy import register_proxy
from bot.random import register_random
from bot.tiktok import register_tiktok
from bot.images import register_images
from bot.github import register_github
from bot.search import register_search
from bot.spamsms import register_spamsms
from bot.lxmanga import register_lxmanga
from bot.funlink import register_funlink
from bot.yeumoney import register_yeumoney
from bot.reaction import register_reaction
from bot.sourceweb import register_sourceweb

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

register_nct(bot)
register_scl(bot)
register_in4(bot)
register_send(bot)
register_time(bot)
register_help(bot)
register_thumb(bot)
register_proxy(bot)
register_random(bot)
register_tiktok(bot)
register_images(bot)
register_github(bot)
register_search(bot)
register_spamsms(bot)
register_lxmanga(bot)
register_funlink(bot)
register_yeumoney(bot)
register_reaction(bot)
register_sourceweb(bot)

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
