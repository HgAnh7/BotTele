caption = """┌───────────────⭓
├ /help: Menu bot
├ /admin: Info admin
├ /time: Check time bot
├ /tiktok: Lấy thông tin video TikTok
├ /thongtin: Lấy thông tin người dùng
├───────────────⭔
├ /github: Info github 🐈‍⬛
├ /images: Lấy url ảnh web 👻
├ /scl: Tải nhạc SoundCloud 🎶
├ /sourceweb: Tải source web 🎃
├───────────────⭔
├ /pussy: 🔞
├ /squeeze: Bóp 🌚
├ /girl: Video gái 😳
├ /butt: Ảnh mông gái 🙅‍♀️
├ /anime: Video anime 🇯🇵
├ /imganime: Ảnh anime 🦄
├ /cosplay: Ảnh cosplay 🧝‍♀️
├ /nude: Ảnh bán thoả thân 🔞
└───────────────⭓
"""

def register_help(bot):
    @bot.message_handler(commands=['help'])
    def send_help(message):
        bot.send_message(
            chat_id=message.chat.id,
            text=caption,
            reply_to_message_id=message.message_id,  # TRẢ LỜI TIN `/help` → có khung
            parse_mode='HTML'  # hoặc bỏ nếu không dùng HTML tag
        )
