import os
import subprocess
from datetime import datetime
import threading

ADMIN_ID = 6379209139
GROUP_ID = [6379209139, 5457864537]
VIP_FILE = "vip.txt"

last_sms_time = {}
last_smsvip_time = {}
sms_process = None
smsvip_process = None

def is_vip(user_id):
    if not os.path.exists(VIP_FILE):
        return False
    with open(VIP_FILE, "r") as f:
        vip_ids = [line.strip() for line in f.readlines()]
    return str(user_id) in vip_ids

def register_spamsms(bot):
    @bot.message_handler(commands=['add'])
    def add(message):
        if message.chat.id != GROUP_ID or message.from_user.id != ADMIN_ID:
            bot.reply_to(message, "❌ Bạn không có quyền sử dụng lệnh này.")
            return

        args = message.text.split()
        if len(args) < 2 or not args[1].isdigit():
            bot.reply_to(message, "❌ Dùng đúng cú pháp: /add [user_id]")
            return

        user_id = args[1].strip()
        if not os.path.exists(VIP_FILE):
            open(VIP_FILE, "w").close()

        with open(VIP_FILE, "r") as f:
            if user_id in f.read():
                bot.reply_to(message, f"ID {user_id} đã có trong danh sách VIP.")
                return

        with open(VIP_FILE, "a") as f:
            f.write(f"{user_id}\n")

        bot.reply_to(message, f"✅ Đã thêm ID {user_id} vào danh sách VIP.")

    @bot.message_handler(commands=['sms'])
    def sms(message):
        if message.chat.id != GROUP_ID:
            return

        user_id = message.from_user.id
        now = datetime.now()

        if user_id in last_sms_time and (now - last_sms_time[user_id]).total_seconds() < 100:
            bot.reply_to(message, "❌ Vui lòng đợi 100s trước khi dùng lại.")
            return

        args = message.text.split()
        if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
            bot.reply_to(message, "❌ Dùng đúng cú pháp: /sms [sđt] [vòng lặp]")
            return

        phone, loops = args[1], int(args[2])
        if len(phone) != 10 or not phone.startswith("0") or loops > 100:
            bot.reply_to(message, "❌ Số điện thoại không hợp lệ hoặc vòng lặp quá giới hạn.")
            return

        last_sms_time[user_id] = now
        bot.reply_to(message, f"⚡*Bắt đầu tấn công SEVER1*\n📱*SĐT:* {phone}\n🌩️*Vòng lặp:* {loops}", parse_mode="Markdown")

        global sms_process
        if sms_process and sms_process.poll() is None:
            sms_process.terminate()

        sms_process = subprocess.Popen(["python3", "bot/spamsms/sms.py", phone, str(loops)])

        def stop_after():
            import time
            time.sleep(200)
            if sms_process and sms_process.poll() is None:
                sms_process.terminate()

        threading.Thread(target=stop_after).start()

    @bot.message_handler(commands=['smsvip'])
    def smsvip(message):
        if message.chat.id != GROUP_ID:
            return

        user_id = message.from_user.id
        now = datetime.now()

        if not is_vip(user_id):
            bot.reply_to(message, "❌ Bạn chưa mua VIP. Liên hệ /admin để mua.")
            return

        if user_id in last_smsvip_time and (now - last_smsvip_time[user_id]).total_seconds() < 60:
            bot.reply_to(message, "❌ Vui lòng đợi 60s trước khi dùng lại.")
            return

        args = message.text.split()
        if len(args) != 3 or not args[1].isdigit() or not args[2].isdigit():
            bot.reply_to(message, "❌ Dùng đúng cú pháp: /smsvip [sđt] [vòng lặp]")
            return

        phone, loops = args[1], int(args[2])
        if len(phone) != 10 or not phone.startswith("0") or loops > 100:
            bot.reply_to(message, "❌ Số điện thoại không hợp lệ hoặc vòng lặp quá giới hạn.")
            return

        last_smsvip_time[user_id] = now
        bot.reply_to(message, f"**smsvip Server 1**\n📱 **Mục tiêu:** {phone}\n🍃 **Vòng lặp:** {loops}", parse_mode="Markdown")

        global smsvip_process
        if smsvip_process and smsvip_process.poll() is None:
            smsvip_process.terminate()

        smsvip_process = subprocess.Popen(["python3", "bot/spamsms/smsvip.py", phone, str(loops)])

        def stop_after():
            import time
            time.sleep(600)
            if smsvip_process and smsvip_process.poll() is None:
                smsvip_process.terminate()

        threading.Thread(target=stop_after).start()
