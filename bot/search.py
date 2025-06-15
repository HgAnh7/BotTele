import requests, html
from bs4 import BeautifulSoup

def register_search(bot):
    @bot.message_handler(commands=['search'])
    def search(message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return bot.reply_to(message, "❌ Vui lòng nhập từ khóa.\nVí dụ: /search cách làm bánh mì")

        query = args[1].strip()
        loading = bot.send_message(message.chat.id, f"🔎 Đang tìm kiếm: <b>{html.escape(query)}</b>")

        try:
            results = search_duckduckgo(query)
            if not results:
                return bot.edit_message_text("❌ Không tìm thấy kết quả.", message.chat.id, loading.message_id)

            reply = f"🔗 <b>Kết quả cho:</b> {html.escape(query)}\n\n" + '\n'.join(
                f"{i+1}. {r['href']}" for i, r in enumerate(results)
            )

            bot.edit_message_text(
                reply,
                message.chat.id,
                loading.message_id,
                disable_web_page_preview=True
            )

        except Exception as e:
            bot.edit_message_text(
                f"❌ Lỗi: {html.escape(str(e))}",
                message.chat.id,
                loading.message_id
            )

def search_duckduckgo(query, max_results=5):
    try:
        res = requests.get(
            f"https://html.duckduckgo.com/html/?q={requests.utils.quote(query)}",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        soup = BeautifulSoup(res.text, 'html.parser')
        results = []

        for a in soup.find_all("a", class_="result__a"):
            href = a.get("href")
            if not href or href.startswith("/l/?kh="): continue  # lọc redirect nội bộ
            results.append({'title': a.get_text(strip=True), 'href': href})
            if len(results) >= max_results: break

        return results
    except Exception:
        return []
