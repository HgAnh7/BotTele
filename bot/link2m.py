# File: link2m.py
import requests
from bs4 import BeautifulSoup
import re

def get_code_from_link2m(url):
    match = re.search(r'link2m\.com/go/(.+)', url.strip().rstrip('/'))
    if not match:
        return None, "Link đéo phải link2m.com/go/xxx"
    
    info_url = f"https://link2m.com/{match.group(1)}/info"
    try:
        headers = {"User-Agent": "Mozilla/5.0", "Accept-Language": "vi-VN,vi;q=0.9", "Referer": "https://link2m.com/",}
        r = requests.get(info_url, headers=headers, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, 'html.parser')
        h3 = soup.find('h3', class_='title')
        if not h3:
            return None, "Không lấy được code (link die hoặc bị block)"
        
        text = h3.get_text(strip=True)
        return text, None
    except:
        return None, "Lỗi kết nối hoặc trang die"

def register_link2m(bot):
	@bot.message_handler(commands=['link2m'])
	def handle_link2m(message):
	    args = message.text.split()
	    if len(args) < 2:
	        bot.reply_to(message, "Dùng: /link2m https://link2m.com/go/xxx")
	        return
	    
	    url = args[1]
	    code, error = get_code_from_link2m(url)
	    
	    if error:
	        bot.reply_to(message, error)
	        return
	    
	    if "SNOTE.VIP" in code.upper():
	        snote_id = code.split('|')[0].strip()
	        new_link = f"https://snote.vip/notes/{snote_id}"
	        bot.reply_to(message, f"✅ SNOTE MỚI:\n{new_link}")
	    else:
	        bot.reply_to(message, f"✅ CODE:\n{code}")
	
	@bot.message_handler(commands=['start'])
	def start(message):
	    bot.reply_to(message, "Gửi /link2m + link link2m để lấy code nhanh!\nVí dụ: /link2m https://link2m.com/go/cHYQD7Fs")
	
	print("Bot đang chạy...")
	