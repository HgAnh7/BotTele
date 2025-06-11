import zipfile
import requests
from io import BytesIO
import concurrent.futures
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def register_lxmanga(bot):
    @bot.message_handler(commands=['lxmanga'])
    def handle_lxmanga(message):
        try:
            chap_url = message.text.split(maxsplit=1)[1].strip()
            if not chap_url.startswith("https://lxmanga"):
                raise ValueError
        except:
            bot.reply_to(message, "❗️ Bạn cần nhập đúng định dạng: /lxmanga <url chương truyện>", parse_mode="Markdown")
            return

        sent_msg = bot.reply_to(message, "🔍 Đang xử lý, vui lòng chờ...")

        try:
            zip_data, total = get_zip_from_chapter(chap_url)

            if total == 0:
                bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text="❌ Không tìm thấy ảnh nào trong trang.")
                return

            zip_data.seek(0)
            file_name = get_story_name_from_url(chap_url) + ".zip"

            # Xóa tin nhắn "đang xử lý"
            bot.delete_message(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id)

            # Gửi file zip
            bot.send_document(
                chat_id=message.chat.id,
                document=zip_data,
                visible_file_name=file_name,
                caption=f"Đã tải xong {total} ảnh từ chương truyện!",
                reply_to_message_id=message.message_id
            )

        except Exception as e:
            bot.edit_message_text(chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, text=f"❌ Đã xảy ra lỗi:\n`{str(e)}`", parse_mode="Markdown")

    def get_zip_from_chapter(chap_url):
        headers = {
            "Referer": chap_url,
            "User-Agent": "Mozilla/5.0",
        }
    
        response = requests.get(chap_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    
        img_divs = soup.select("div.text-center div.lazy")
        img_urls = [div.get("data-src") for div in img_divs if div.get("data-src")]
    
        zip_buffer = BytesIO()
        story_name = get_story_name_from_url(chap_url)
        chapter_name = get_chapter_name_from_url(chap_url)
    
        def download_image(url_idx_tuple):
            url, idx = url_idx_tuple
            try:
                img_data = requests.get(url, headers=headers, timeout=10).content
                ext = url.split(".")[-1].split("?")[0]
                filename = f"{idx+1:03d}.{ext}"
                zip_path = f"{story_name}/{chapter_name}/{filename}"
                return (zip_path, img_data)
            except Exception:
                return None  # Bỏ qua ảnh lỗi
    
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(download_image, [(url, i) for i, url in enumerate(img_urls)])
    
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            count = 0
            for item in results:
                if item:
                    zipf.writestr(item[0], item[1])
                    count += 1
    
        return zip_buffer, count
    
    def get_story_name_from_url(url):
        path = urlparse(url).path.strip("/")
        path_parts = path.split("/")
        if len(path_parts) >= 2 and path_parts[0].lower() == "truyen":
            return path_parts[1].replace("-", " ")
        return path.replace("/", "_")

    def get_chapter_name_from_url(url):
        path_parts = urlparse(url).path.strip("/").split("/")
        # Luôn lấy phần cuối làm tên chương
        return path_parts[-1].replace("-", " ")
