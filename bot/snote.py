import requests
from bs4 import BeautifulSoup

def register_snote(bot):
	@bot.message_handler(commands=['snote'])
	def handle_snote(message):
		text = message.text.split()
		if len(text) != 2:
			bot.reply_to(message, 'Sử dụng: /snote <ID> (ví dụ: /snote 96ZK18)')
			return

		note_id = text[1].strip()
		url = f'https://snote.vip/notes/{note_id}'

		try:
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
			}

			response = requests.get(url, headers=headers)
			response.raise_for_status()

			soup = BeautifulSoup(response.text, 'html.parser')

			# Tìm <h5> chứa note time
			note_time = soup.find('h5')
			if note_time:
				time_text = note_time.get_text().strip()
			else:
				time_text = 'Không tìm thấy thời gian note.'

			# Tìm <p> sau <h5> chứa content (link hoặc text)
			content_tag = soup.find('p')  # Hoặc note_time.next_sibling if cần chính xác hơn
			if content_tag:
				content = content_tag.get_text().strip()
				if content == '/' or not content:
					bot.reply_to(message, f'Note tại {url} có thể chưa sẵn sàng hoặc hết hạn (nội dung rỗng: "{content}"). Thời gian: {time_text}')
				else:
					bot.reply_to(message, f'Nội dung từ {url}:\n{content}\nThời gian: {time_text}')
			else:
				bot.reply_to(message, f'Không tìm thấy nội dung chính ở {url}. Có thể cấu trúc trang thay đổi.')

		except requests.exceptions.RequestException as e:
			bot.reply_to(message, f'Lỗi khi lấy dữ liệu từ {url}: {str(e)}. Thử kiểm tra kết nối hoặc headers.')
