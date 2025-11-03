import re
import zipfile
import requests
from io import BytesIO
from telebot import types
from bs4 import BeautifulSoup

# Lưu thông tin theo chat để tránh lẫn lộn
chat_data = {}

def get_name_manga(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.find("title").text.strip()

def get_author(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    divs = soup.find_all("div", class_="mt-2")
    for div in divs:
        if "Tác giả" in div.text:
            a = div.find("a")
            if a:
                href = a.get("href", "")
                name = a.text.strip()
                return f'<a href="https://lxmanga.my{href}">{name}</a>'
    return None

def get_cover(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    cover_div = soup.select_one(".cover")
    if not cover_div:
        return None
        
    style = cover_div.get("style", "")
    match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style)
    if not match:
        return None
        
    headers = {"Referer": url, "User-Agent": "Mozilla/5.0"}
    resp = requests.get(match.group(1), headers=headers, timeout=15)
    
    cover_file = BytesIO(resp.content)
    cover_file.name = "cover.jpg"
    return cover_file

def get_chapters_and_urls(url):
    response = requests.get(url, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Lấy tên chương
    chapters = []
    img_tags = soup.find_all("img", alt="untag-r")
    for img in img_tags:
        span = img.find_next("span")
        if span:
            chapters.append(span.get_text(strip=True))
    
    # Lấy URL chương  
    urls = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "")
        if href.startswith("/truyen/") and href.count("/") == 3:
            urls.append(f"https://lxmanga.my{href}")

    if len(urls) <= 1:
        return [], []
    return chapters, urls[1:]

def get_chapter_images(chapter_url):
    headers = {"Referer": chapter_url, "User-Agent": "Mozilla/5.0"}
    response = requests.get(chapter_url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    images = []
    for index, div in enumerate(soup.select("div#image-container.lazy"), 1):
        img_url = div.get("data-src")
        if img_url:
            r = requests.get(img_url, headers=headers, timeout=15)
            img = BytesIO(r.content)
            img.name = f"{index:03}.jpg"
            images.append(img)
    return images

def create_chapter_zip(manga_name, chapter_title, chapter_url, cover_file=None):
    zip_buf = BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zipf:
        if cover_file:
            zipf.writestr(f"{manga_name}/cover.jpg", cover_file.getvalue())
        images = get_chapter_images(chapter_url)
        if not images:
            return None, "Không có ảnh"
            
        for i, img in enumerate(images, 1):
            path = f"{manga_name}/{chapter_title}/{i}.jpg"
            zipf.writestr(path, img.getvalue())

    zip_buf.seek(0, 2)
    if zip_buf.tell() > 50 * 1024 * 1024:
        return None, "File vượt quá 50MB, không thể gửi qua Telegram"
    
    zip_buf.seek(0)
    zip_buf.name = "lxm.zip"
    return zip_buf, None

def register_lx(bot):
    @bot.message_handler(commands=['lx'])
    def handle_manga_request(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            bot.reply_to(message, "Nhập URL truyện cần tải.\nVí dụ: /lx https://lxmanga.my/truyen/...")
            return

        url = args[1]
        chat_id = message.chat.id
        
        if not url.startswith("https://lxmanga."):
            bot.reply_to(message, "Chỉ hỗ trợ lxmanga")
            return

        # Hiển thị đang xử lý
        processing_msg = bot.reply_to(message, "Đang tải thông tin truyện...")

        try:
            manga_name = get_name_manga(url)
            chapters, chapter_urls = get_chapters_and_urls(url)
            cover = get_cover(url)
            author = get_author(url)
            if not chapters:
                bot.edit_message_text(
                    "Không tìm thấy chương nào!", 
                    chat_id, 
                    int(processing_msg.message_id)  # Ép int
                )
                return

            # Lưu data cho chat này
            chat_data[chat_id] = {
                'manga_name': manga_name,
                'chapters': chapters,
                'urls': chapter_urls,
                'manga_url': url,
                'cover': cover,
                'author': author
            }

            # Tạo keyboard chọn chương
            markup = types.InlineKeyboardMarkup(row_width=3)
            
            # Tạo nút cho từng chương (đảo ngược để chương mới nhất ở trên)
            buttons = []
            for i in range(len(chapters)-1, -1, -1):
                buttons.append(types.InlineKeyboardButton(
                    text=chapters[i], 
                    callback_data=f"ch|{i}"
                ))
            
            # Chia thành hàng 3 nút
            for i in range(0, len(buttons), 3):
                markup.row(*buttons[i:i+3])
            
            # Nút tải tất cả
            if len(chapters) > 1:
                markup.add(types.InlineKeyboardButton("Tải tất cả", callback_data="all"))

            # Xóa tin nhắn đang xử lý
            bot.delete_message(chat_id, int(processing_msg.message_id))  # Ép int
            
            author = author or 'Không rõ'
            caption = f"""<b>{manga_name}</b>
 » <b>Tác giả:</b> {author}
 » <b>Số chương:</b> {len(chapters)}

 👇 Chọn chương cần tải:"""
            
            if cover:
                bot.send_photo(chat_id, cover, caption=caption, reply_markup=markup, parse_mode='HTML')
            else:
                bot.send_message(chat_id, caption, reply_markup=markup, disable_web_page_preview=True, parse_mode='HTML')
                
        except Exception as e:
            bot.edit_message_text(
                f"Lỗi: {e}", 
                chat_id, 
                int(processing_msg.message_id)  # Ép int
            )

    # Xử lý khi chọn 1 chương
    @bot.callback_query_handler(func=lambda call: call.data.startswith("ch|"))
    def handle_single_chapter(call):
        chat_id = call.message.chat.id
        msg_id = int(call.message.message_id)  # Ép int ngay
        chapter_index = int(call.data.split("|")[1])
        
        if chat_id not in chat_data:
            bot.answer_callback_query(call.id, "Hết hạn, thử lại!", show_alert=True)
            return
        
        data = chat_data[chat_id]
        chapter_title = data['chapters'][chapter_index]
        chapter_url = data['urls'][chapter_index]
        cover = data.get('cover')
        
        # Edit tin nhắn thành trạng thái đang tải
        bot.edit_message_caption(
            caption=f"Đang tải: <b>{chapter_title}</b>...",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        
        try:
            manga_name = data['manga_name']
            zip_file, error = create_chapter_zip(manga_name, chapter_title, chapter_url, cover)
            if error:
                bot.edit_message_caption(
                    caption=f"Lỗi tải chương: {error}",
                    chat_id=chat_id,
                    message_id=msg_id,
                    parse_mode='HTML'
                )
                return

            author = data.get('author', 'Không rõ')
            manga_url = data['manga_url']
            caption = f"<b><a href='{manga_url}'>{manga_name}</a></b>\nTác giả: {author}\n{chapter_title}"
            bot.send_document(chat_id, zip_file, caption=caption, parse_mode='HTML')
            bot.delete_message(chat_id, msg_id)  # Ép int đã có
            zip_file.close()
            chat_data.pop(chat_id, None)

        except Exception as e:
            bot.edit_message_caption(
                caption=f"Lỗi: {e}",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode='HTML'
            )

    # Xử lý tải tất cả chương
    @bot.callback_query_handler(func=lambda call: call.data == "all")
    def handle_all_chapters(call):
        chat_id = call.message.chat.id
        msg_id = int(call.message.message_id)  # Ép int ngay
        
        if chat_id not in chat_data:
            bot.answer_callback_query(call.id, "Hết hạn, thử lại!", show_alert=True)
            return
        
        data = chat_data[chat_id]
        total = len(data['chapters'])
        
        # Edit tin nhắn thành trạng thái đang tải tất cả
        bot.edit_message_caption(
            caption=f"Đang tải tất cả {total} chương...",
            chat_id=chat_id,
            message_id=msg_id,
            parse_mode='HTML'
        )
        bot.answer_callback_query(call.id)
        
        try:
            manga_name = data['manga_name']
            cover = data.get('cover')
            
            # Lặp qua từng chương và tạo file zip riêng
            for i, (chapter_title, chapter_url) in enumerate(zip(data['chapters'][::-1], data['urls'][::-1])):
                # Update progress
                progress = int((i + 1) / total * 100)
                try:
                    bot.edit_message_caption(
                        caption=f"Đang tải... {i+1}/{total} ({progress}%)\n{chapter_title}",
                        chat_id=chat_id,
                        message_id=msg_id,
                        parse_mode='HTML'
                    )
                except:
                    pass  # Bỏ qua lỗi edit nếu Telegram rate limit
                
                # Tạo file zip cho chương này
                zip_file, error = create_chapter_zip(manga_name, chapter_title, chapter_url, cover)
                
                if error:
                    bot.send_message(chat_id, f"Lỗi tải {chapter_title}: {error}")
                    continue
                
                author = data.get('author', 'Không rõ')
                manga_url = data['manga_url']
                # Gửi file zip của chương
                caption = f"<b><a href='{manga_url}'>{manga_name}</a></b>\nTác giả: {author}\n{chapter_title} ({i+1}/{total})"
                bot.send_document(chat_id, zip_file, caption=caption, parse_mode='HTML')
                zip_file.close()
                
            bot.delete_message(chat_id, msg_id)  # Ép int đã có
            chat_data.pop(chat_id, None)
            
        except Exception as e:
            bot.edit_message_caption(
                caption=f"Lỗi tải tất cả: {e}",
                chat_id=chat_id,
                message_id=msg_id,
                parse_mode='HTML'
            )