import telebot
import requests
from bs4 import BeautifulSoup
import re


# ==== HÀM GIẢI LINK ====
def convert_go_to_info(url):
    url = url.strip().rstrip('/')
    match = re.search(r'link2m\.com/go/(.+)', url)
    if match:
        return f"https://link2m.com/{match.group(1).strip()}/info"
    raise ValueError("❌ Link không hợp lệ. Hãy gửi link dạng link2m.com/go/xxx")

def get_code_and_final_content(short_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept-Language": "vi-VN,vi;q=0.9",
        "Referer": "https://link2m.com/",
    }

    session = requests.Session()
    session.headers.update(headers)
    try:
        info_url = convert_go_to_info(short_url)
        r1 = session.get(info_url, timeout=15)
        r1.raise_for_status()

        soup = BeautifulSoup(r1.text, 'html.parser')
        h3 = soup.find('h3', class_='title')
        raw_code = h3.get_text(strip=True) if h3 else "Không thấy code"

        # Nếu là SNOTE
        if "SNOTE.VIP" in raw_code.upper():
            snote_id = raw_code.split('|')[0].strip()
            final_url = f"https://snote.vip/notes/{snote_id}"
            r_note = session.get(final_url)
            note_soup = BeautifulSoup(r_note.text, 'html.parser')
            content_div = note_soup.find('div', class_='note-content') or note_soup.find('pre') or note_soup.find('code')
            note_text = content_div.get_text(strip=True) if content_div else "Note private hoặc die"
            return raw_code, final_url, note_text

        # Không phải snote
        wrapper = soup.find('div', id='captcha-html-wrapper')
        if not wrapper:
            return raw_code, None, "Không unlock được (link die hoặc bị bảo vệ)"

        alias = wrapper['data-alias']
        code_token = wrapper['data-code']
        unlock_url = "https://link2m.com/links/go"
        payload = {"alias": alias, "code": code_token}

        r2 = session.post(unlock_url, data=payload, headers={"X-Requested-With": "XMLHttpRequest"})
        if r2.status_code == 200 and r2.json().get('success'):
            real_url = r2.json().get('url')
            r3 = session.get(real_url, allow_redirects=True)
            if 'text' in r3.headers.get('Content-Type', '') or r3.status_code == 200:
                full_text = r3.text.strip()[:2000]
                return raw_code, real_url, full_text
            else:
                return raw_code, real_url, "Nội dung nhị phân hoặc trang web"
        else:
            return raw_code, None, "Unlock fail hoặc token hết hạn"
    except Exception as e:
        return None, None, f"Lỗi: {e}"

def register_link2m(bot):
# ==== LỆNH BẮT LINK ====
	@bot.message_handler(commands=['start'])
	def send_welcome(message):
	    bot.reply_to(message, "👋 Gửi link dạng https://link2m.com/go/... để mình giải giúp!")
	
	@bot.message_handler(func=lambda msg: 'link2m.com/go/' in msg.text)
	def handle_link(message):
	    link = message.text.strip()
	    bot.send_message(message.chat.id, "⏳ Đang xử lý link, đợi xíu nha...")
	    code, final_link, content = get_code_and_final_content(link)
	
	    if code is None:
	        bot.send_message(message.chat.id, f"❌ {content}")
	        return
	
	    reply = f"<b>🔍 Kết quả giải mã:</b>\n\n"
	    reply += f"🧩 <b>Code:</b> <code>{code}</code>\n"
	    if final_link:
	        reply += f"🌐 <b>Link thật:</b> {final_link}\n"
	    reply += f"\n📝 <b>Nội dung:</b>\n<code>{content[:1900]}</code>"
	    bot.send_message(message.chat.id, reply)
	
	# ==== CHẠY BOT ====
	print("✅ Bot link2m.com đã khởi động...")