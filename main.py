# main.py #
import os
import telebot

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML, skip_pending = True)

# Luôn phải ở đầu để đạt hiệu quả tốt nhất
from bot.reaction import register_reaction
register_reaction(bot)

from bot.link2m import register_link2m
register_link2m(bot)

from bot.encode import register_encode
register_encode(bot)

from bot.pyf import register_pyf
register_pyf(bot)

# from bot.nct import register_nct
# register_nct(bot)

from bot.share import register_share
register_share(bot)

from bot.img import register_img
register_img(bot)

from bot.img1 import register_img1
register_img1(bot)

from bot.cosplay import register_cosplay
register_cosplay(bot)

from bot.scl import register_scl
register_scl(bot)

from bot.in4 import register_in4
register_in4(bot)

from bot.r34 import register_r34
register_r34(bot)

from bot.pixxx import register_pixxx
register_pixxx(bot)

from bot.send import register_send
register_send(bot)

from bot.time import register_time
register_time(bot)

from bot.help import register_help
register_help(bot)

from bot.nekos import register_nekos
register_nekos(bot)

from bot.thumb import register_thumb
register_thumb(bot)

from bot.proxy import register_proxy
register_proxy(bot)

from bot.random import register_random
register_random(bot)

from bot.tiktok import register_tiktok
register_tiktok(bot)

from bot.images import register_images
register_images(bot)

from bot.github import register_github
register_github(bot)

from bot.search import register_search
register_search(bot)

from bot.meme import register_meme
register_meme(bot)

from bot.spamsms import register_spamsms
register_spamsms(bot)

from bot.lx import register_lx
register_lx(bot)

from bot.lxmanga import register_lxmanga
register_lxmanga(bot)

# from bot.funlink import register_funlink
from funlink import register_funlink
register_funlink(bot)

from bot.yeumoney import register_yeumoney
register_yeumoney(bot)

from bot.sourceweb import register_sourceweb
register_sourceweb(bot)

if __name__ == '__main__':
    print("Bot đang chạy...")
    bot.infinity_polling()
