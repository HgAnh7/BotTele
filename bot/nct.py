import io
import requests
import threading
from telebot import types

nct_data = {}


def search_music(keyword):
	params = {
		'keyword': keyword,
		'pageindex': '1',
		'pagesize': 30,
		'correct': 'true',
	}
	response = requests.post(
		'https://graph.nhaccuatui.com/api/v1/search/song',
		params=params,
	)
	return response.json()


def register_nct(bot):
	@bot.message_handler(commands=['nct'])
	def nhaccuatui(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2:
			bot.reply_to(message, "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /nct Tên bài hát")
			return

		keyword = args[1]
		data = search_music(keyword)
		songs = data.get('data', {}).get('songs') if data else None
		if not songs:
			bot.reply_to(message, "🚫 Không tìm thấy bài hát nào khớp với từ khóa.")
			return

		songs = songs[:10]

		# Tạo response text
		lines = ["<b>🎵 Kết quả tìm kiếm trên NhacCuaTui</b>\n"]
		for i, song in enumerate(songs):
			lines.append(
				f"<b>{i + 1}. {song.get('name')}</b>\n"
				f" <b>» Ca sĩ:</b> {song.get('artistName')}\n"
			)
		lines.append("<b>💡 Chọn số bài hát bạn muốn tải!</b>")
		response_text = "\n".join(lines)

		# Tạo inline keyboard chọn bài hát
		markup = types.InlineKeyboardMarkup(row_width=5)
		markup.add(*[
			types.InlineKeyboardButton(str(i + 1), callback_data=f"nct_song_{message.from_user.id}_{i}")
			for i in range(len(songs))
		])

		sent = bot.reply_to(message, response_text, reply_markup=markup)
		key = f"{message.from_user.id}_{sent.message_id}"
		nct_data[key] = {
			"songs": songs,
			"chat_id": sent.chat.id,
			"command_msg_id": message.message_id,
		}

		# Tự động xóa sau 2 phút nếu chưa chọn
		def delete_if_not_used():
			if key in nct_data:
				try:
					bot.delete_message(sent.chat.id, sent.message_id)
					bot.delete_message(sent.chat.id, nct_data[key]["command_msg_id"])
				except Exception:
					pass
				nct_data.pop(key, None)

		threading.Timer(120, delete_if_not_used).start()

	# Bước 1: chọn bài hát -> hiện danh sách chất lượng
	@bot.callback_query_handler(func=lambda call: call.data.startswith('nct_song_'))
	def handle_song_selection(call):
		try:
			parts = call.data.split('_')
			user_id = int(parts[2])
			song_index = int(parts[3])

			if call.from_user.id != user_id:
				bot.answer_callback_query(call.id, "❌ Bạn không có quyền sử dụng nút này!", show_alert=True)
				return

			key = f"{user_id}_{call.message.message_id}"
			data = nct_data.get(key)
			if not data:
				bot.answer_callback_query(call.id, "❌ Dữ liệu đã hết hạn hoặc đã dùng rồi!", show_alert=True)
				return

			songs = data["songs"]
			if song_index >= len(songs):
				bot.answer_callback_query(call.id, "❌ Lựa chọn không hợp lệ!", show_alert=True)
				return

			song = songs[song_index]
			streams = song.get('streamURL') or []
			if not streams:
				bot.answer_callback_query(call.id, "❌ Bài hát này không có link tải!", show_alert=True)
				return

			data["song_index"] = song_index

			markup = types.InlineKeyboardMarkup(row_width=len(streams))
			markup.add(*[
				types.InlineKeyboardButton(
					s.get('typeUI', f'Chất lượng {i + 1}'),
					callback_data=f"nct_quality_{user_id}_{i}"
				)
				for i, s in enumerate(streams)
			])

			bot.edit_message_text(
				f"<b>{song.get('name')}</b>\n👤 Ca sĩ: {song.get('artistName')}\n\n<b>💡 Chọn chất lượng nhạc:</b>",
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
				reply_markup=markup,
			)
			bot.answer_callback_query(call.id)

		except Exception as e:
			bot.answer_callback_query(call.id, f"❌ Có lỗi xảy ra: {str(e)}", show_alert=True)

	# Bước 2: chọn chất lượng -> tải và gửi nhạc
	@bot.callback_query_handler(func=lambda call: call.data.startswith('nct_quality_'))
	def handle_quality_selection(call):
		try:
			parts = call.data.split('_')
			user_id = int(parts[2])
			quality_index = int(parts[3])

			if call.from_user.id != user_id:
				bot.answer_callback_query(call.id, "❌ Bạn không có quyền sử dụng nút này!", show_alert=True)
				return

			key = f"{user_id}_{call.message.message_id}"
			data = nct_data.pop(key, None)
			if not data or "song_index" not in data:
				bot.answer_callback_query(call.id, "❌ Dữ liệu đã hết hạn hoặc đã dùng rồi!", show_alert=True)
				return

			song = data["songs"][data["song_index"]]
			streams = song.get('streamURL') or []
			if quality_index >= len(streams):
				bot.answer_callback_query(call.id, "❌ Lựa chọn không hợp lệ!", show_alert=True)
				return

			song_name = song.get('name')
			artist_name = song.get('artistName')
			thumbnail_url = song.get('image')
			audio_url = streams[quality_index].get('download')
			quality_label = streams[quality_index].get('typeUI')

			bot.answer_callback_query(call.id, f"🎵 Đang tải: {song_name}")

			# Gửi thông báo đang tải
			bot.edit_message_text(
				f"🧭 Đang tải: <b>{song_name}</b>\n👤 Ca sĩ: {artist_name}\n🎚 Chất lượng: {quality_label}\n\n⏳ Vui lòng chờ...",
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
			)

			if not audio_url:
				bot.edit_message_text(
					"🚫 Không tìm thấy nguồn audio.",
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
				)
				return

			resp = requests.get(audio_url, stream=True)
			resp.raise_for_status()

			content_length = int(resp.headers.get('Content-Length', 0))
			if content_length > 50 * 1024 * 1024:  # Giới hạn 50MB
				bot.edit_message_text(
					"🚫 File nhạc quá lớn (>50MB) nên không thể gửi qua Telegram.",
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
				)
				return

			audio = io.BytesIO(resp.content)
			audio.name = f"{song_name}.mp3"

			caption = f"""<blockquote>⭔───────────────⭓
 <b>{song_name}</b>
 » <b>Ca sĩ:</b> {artist_name}
 » <b>Chất lượng:</b> {quality_label}
 » <b>Nguồn:</b> NhacCuaTui 🎶 
⭓───────────────⭔</blockquote>"""

			# Gửi thông tin + file nhạc
			bot.send_photo(call.message.chat.id, thumbnail_url, caption=caption)
			bot.send_audio(
				call.message.chat.id,
				audio,
				title=song_name,
				performer=artist_name,
			)

			# Xóa thông báo đang tải
			try:
				bot.delete_message(call.message.chat.id, call.message.message_id)
			except Exception:
				pass

		except Exception as e:
			bot.answer_callback_query(call.id, f"❌ Có lỗi xảy ra: {str(e)}", show_alert=True)
