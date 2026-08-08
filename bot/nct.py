import io
import requests
import threading
from telebot import types

API_SEARCH_URL = "https://graph.nhaccuatui.com/api/v1/search/song"
nct_data = {}

def search_music(keyword):
	try:
		params = {
			"keyword": keyword,
			"pageindex": 1,
			"pagesize": 30,
			"correct": "true",
		}
		response = requests.get(
			API_SEARCH_URL,
			params=params,
			timeout=10,
		)
		return response.json()
	except Exception:
		return None

def get_best_stream_url(song):
	"""Chọn link tải chất lượng cao nhất có sẵn (dựa theo typeUI, vd '320', '128')."""
	streams = song.get('streamURL') or []
	if not streams:
		return None

	def quality_score(s):
		type_ui = (s.get('typeUI') or '').strip()
		digits = ''.join(ch for ch in type_ui if ch.isdigit())
		return int(digits) if digits else 0

	best = max(streams, key=quality_score)
	return best.get('download')


def register_nct(bot):
	@bot.message_handler(commands=['nct'])
	def nhaccuatui(message):
		args = message.text.split(maxsplit=1)
		if len(args) < 2:
			bot.reply_to(message, "🚫 Vui lòng nhập tên bài hát muốn tìm kiếm.\nVí dụ: /nct Tên bài hát")
			return

		keyword = args[1]
		result = search_music(keyword)
		songs = (result or {}).get('data', {}).get('songs') or []
		if not songs:
			bot.reply_to(message, "🚫 Không tìm thấy bài hát nào khớp với từ khóa.")
			return

		songs = [song for song in songs if song.get('image')]
		songs = songs[:10]
		if not songs:
			bot.reply_to(message, "🚫 Không tìm thấy bài hát nào có hình ảnh.")
			return

		# Tạo response text
		lines = ["<b>🎵 Kết quả tìm kiếm trên NhacCuaTui</b>\n"]
		for i, song in enumerate(songs):
			lines.append(
				f"<b>{i + 1}. {song.get('name', 'Không rõ')}</b>\n"
				f" <b>» Ca sĩ:</b> {song.get('artistName', 'Không rõ')}\n"
			)
		lines.append("<b>💡 Chọn số bài hát bạn muốn tải!</b>")
		response_text = "\n".join(lines)

		# Tạo inline keyboard
		markup = types.InlineKeyboardMarkup(row_width=5)
		markup.add(*[
			types.InlineKeyboardButton(str(i + 1), callback_data=f"nct_{message.from_user.id}_{i}")
			for i in range(len(songs))
		])

		# Gửi message với inline keyboard
		sent = bot.reply_to(message, response_text, reply_markup=markup)
		# Lưu data cho callback
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

	@bot.callback_query_handler(func=lambda call: call.data.startswith('nct_'))
	def handle_nhaccuatui_callback(call):
		try:
			# Parse callback data
			parts = call.data.split('_')
			user_id = int(parts[1])
			song_index = int(parts[2])

			# Kiểm tra quyền truy cập
			if call.from_user.id != user_id:
				bot.answer_callback_query(call.id, "❌ Bạn không có quyền sử dụng nút này!", show_alert=True)
				return

			key = f"{user_id}_{call.message.message_id}"
			data = nct_data.pop(key, None)
			if not data:
				bot.answer_callback_query(call.id, "❌ Dữ liệu đã hết hạn hoặc đã dùng rồi!", show_alert=True)
				return

			songs = data["songs"]
			# Kiểm tra index hợp lệ
			if song_index >= len(songs):
				bot.answer_callback_query(call.id, "❌ Lựa chọn không hợp lệ!", show_alert=True)
				return

			song = songs[song_index]
			song_name = song.get('name', 'Không rõ')
			artist_name = song.get('artistName', 'Không rõ')

			bot.answer_callback_query(call.id, f"🎵 Đang tải: {song_name}")
			bot.edit_message_text(
				f"🧭 Đang tải: <b>{song_name}</b>\n👤 Ca sĩ: {artist_name}\n\n⏳ Vui lòng chờ...",
				chat_id=call.message.chat.id,
				message_id=call.message.message_id,
			)

			# Lấy audio URL và thumbnail
			audio_url = get_best_stream_url(song)
			thumbnail_url = song.get('image', '')
			if not audio_url or not thumbnail_url:
				bot.edit_message_text(
					"🚫 Không tìm thấy nguồn audio hoặc thumbnail.",
					chat_id=call.message.chat.id,
					message_id=call.message.message_id,
				)
				return

			caption = f"""<blockquote>⭔───────────────⭓
 <b>{song_name}</b>
 » <b>Ca sĩ:</b> {artist_name}
 » <b>Nguồn:</b> NhacCuaTui 🎶 
⭓───────────────⭔</blockquote>"""

			resp = requests.get(audio_url, headers=HEADERS, stream=True, timeout=30)
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

			# Gửi ảnh thumbnail và audio
			bot.send_photo(call.message.chat.id, thumbnail_url, caption=caption)
			bot.send_audio(
				call.message.chat.id,
				audio,
				title=song_name,
				performer=artist_name,
			)

			# Xóa tin nhắn kết quả tìm kiếm
			try:
				bot.delete_message(call.message.chat.id, call.message.message_id)
			except Exception:
				pass

		except Exception as e:
			bot.answer_callback_query(call.id, f"❌ Có lỗi xảy ra: {str(e)}", show_alert=True)
