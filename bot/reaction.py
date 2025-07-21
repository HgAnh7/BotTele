import random
from telebot import types
from config import GROUP_ID

emoji_list = ['👍', '👎', '❤️', '🔥', '🥰', '👏', '😁', '🤔', '🤯', '😱', '🤬', '😢', '🎉', '🤩', '🤮', '💩', '🙏', '👌',
              '🕊️', '🤡', '🥱', '🥴', '😍', '🐳', '❤️‍🔥', '🌚', '🌭', '💯', '🤣', '⚡', '🍌', '🏆', '💔', '🤨', '😐', '🍓',
              '🍾', '💋', '🖕', '😈', '😴', '😭', '🤓', '👻', '👨‍💻', '👀', '🎃', '🙈', '😇', '😨', '🤝', '✍️', '🤗', '🫡',
              '🎅', '🎄', '☃️', '💅', '🤪', '🗿', '🆒', '💘', '🙉', '🦄', '😘', '💊', '🙊', '😎', '👾', '🤷‍♂️', '🤷', '🤷‍♀️', '😡']

def register_reaction(bot):
    # 🎯 Xử lý mọi tin nhắn
    @bot.message_handler(
        func=lambda m: not (m.content_type == 'text' and m.text.startswith('/')),
        content_types=['text', 'photo', 'video', 'sticker', 'audio', 'document', 'voice']
    )
    def handle_all_messages(message):
        # if message.chat.id not in GROUP_ID:
        #     return

        emoji = random.choice(emoji_list)
        try:
            bot.set_message_reaction(
                message.chat.id,
                message.message_id,
                reaction=[types.ReactionTypeEmoji(emoji)]
            )
        except Exception:
            pass