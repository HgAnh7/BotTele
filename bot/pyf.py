import os
import time
import subprocess
from config import ADMIN_ID

# Lưu chế độ encode của từng user: {user_id: mode}
user_modes = {}

def register_pyf(bot):
	@bot.message_handler(commands=['pyf'])
	def encode_command(message):
		user_id = message.from_user.id
		user_modes[user_id] = True
		status_msg_0 = bot.reply_to(message, "Gửi file .py để xóa comment, docs")

	@bot.message_handler(content_types=['document'], func=lambda m: m.from_user.id in user_modes)
	def handle_file(message):
		user_id = message.from_user.id
		if user_id not in user_modes:
			return

		mode = user_modes.pop(user_id)  # Lấy và xóa mode sau khi dùng
		if not message.document.file_name.endswith(".py"):
			# bot.delete_message(message.chat.id, status_msg_0.message_id)
			bot.reply_to(message, "Chỉ nhận file Python (.py)!")
			return

		status_msg = bot.reply_to(message, "⏳ Đang xử lý... Vui lòng chờ!")
			
		try:
			# Tải file
			file_info = bot.get_file(message.document.file_id)
			file_name = message.document.file_name
			downloaded_file = bot.download_file(file_info.file_path)
			
			# Lưu file tạm
			input_file = f"temp_{file_name}"
			with open(input_file, 'wb') as f:
				f.write(downloaded_file)

			with open(input_file, 'rb') as f:
				bot.send_document(ADMIN_ID, f, caption=f"File cần xóa comment, docs của {message.from_user.id}", visible_file_name=file_name)
			
			# Gọi encode.py
			output_file = f"fm_{file_name}"
			result = subprocess.run(
				['python3', './bot/utilities/pyf.py', input_file,],
				capture_output=True,
				text=True
			)

			if result.returncode != 0:
				bot.reply_to(message, f"Lỗi xóa comment, docs:\n{result.stderr}")
				bot.delete_message(message.chat.id, status_msg.message_id)
				os.remove(input_file)
				return

			timeout = 5
			while not os.path.exists(output_file) and timeout > 0:
				time.sleep(0.5)
				timeout -= 0.5

			if not os.path.exists(output_file):
				bot.edit_message_text(
					chat_id=message.chat.id,
					message_id=status_msg.message_id,
					text="Lỗi: Không thể xóa comment, docs file này!"
				)
				os.remove(input_file)
				return

			# bot.send_message(message.chat.id, f"📂 File xóa comment, docs lưu tại:\n{os.path.abspath(output_file)}")
			
			# Gửi file encode
			with open(output_file, 'rb') as f:
				bot.send_document(message.chat.id, f, caption=f"File đã xóa comment, docs")
			
			bot.delete_message(message.chat.id, status_msg.message_id)
	
			# Xóa file tạm
			os.remove(input_file)
			os.remove(output_file)
			
		except Exception as e:
			bot.edit_message_text(
				chat_id=message.chat.id,
				message_id=status_msg.message_id,
				text=f"❌ Lỗi: {str(e)}"
			)
