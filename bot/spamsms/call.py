import json
import time
from datetime import datetime, timezone
import requests
import random, string
import uuid
import sys
def generate_request_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

def debug_request(phone):    
    print("="*60)
    print("🔍 BẮT ĐẦU DEBUG API REQUEST")
    print("="*60)
    
    cookies = {
        "__sbref": "hgpyjywadlykgkoiavkyouqetxuxcpwhpxdqandf",
        "_cabinet_key": "SFMyNTY.g3QAAAACbQAAABBvdHBfbG9naW5fcGFzc2VkZAAFZmFsc2VtAAAABXBob25lbQAAAAs4NDkxNDkwMTk2Ng.nD_8NLs-CZ7IqIV4JqSpmnAsPVAC0r0WuzMgua9OO1U",
    }
    
    headers_get = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "vi,en-US;q=0.9,en;q=0.8",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "referer": "https://vayxanh.com/",
    }
    
    x_request_id = generate_request_id()
    headers_post = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "vi,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json;charset=utf-8",
        "origin": "https://lk.vayxanh.com",
        "referer": f"https://lk.vayxanh.com/?phone={phone}&amount=2000000&term=7",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "x-request-id": x_request_id,
    }
    
    try:
        # === BƯỚC 1: GỬI GET REQUEST ===
        print("\n📤 BƯỚC 1: Gửi GET request để lấy session")
        print("-" * 60)
        
        params = {
            "phone": phone,
            "amount": "2000000",
            "term": "7",
            "utm_source": "direct_vayxanh",
            "utm_medium": "organic",
            "utm_campaign": "direct_vayxanh",
            "utm_content": "mainpage_submit",
        }
        
        print(f"URL: https://lk.vayxanh.com/")
        print(f"Params: {json.dumps(params, indent=2, ensure_ascii=False)}")
        
        response_get = requests.get(
            "https://lk.vayxanh.com/",
            params=params,
            cookies=cookies,
            headers=headers_get,
            timeout=15
        )
        
        print(f"\n✅ GET Response:")
        print(f"  - Status Code: {response_get.status_code}")
        print(f"  - Content-Type: {response_get.headers.get('content-type')}")
        print(f"  - Cookies nhận được: {dict(response_get.cookies)}")
        
        # Cập nhật cookies từ response
        cookies.update(response_get.cookies.get_dict())
        
        # === BƯỚC 2: GỬI POST REQUEST ===
        print("\n📤 BƯỚC 2: Gửi POST request để gửi OTP")
        print("-" * 60)
        
        json_data = {
            "data": {
                "phone": phone,
                "code": "resend",
                "channel": "ivr",  # hoặc "sms"
            }
        }
        
        print(f"URL: https://lk.vayxanh.com/api/4/client/otp/send")
        print(f"Body: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        print(f"Headers: {json.dumps(headers_post, indent=2, ensure_ascii=False)}")
        
        response_post = requests.post(
            "https://lk.vayxanh.com/api/4/client/otp/send",
            cookies=cookies,
            headers=headers_post,
            json=json_data,
            timeout=15
        )
        
        print(f"\n✅ POST Response:")
        print(f"  - Status Code: {response_post.status_code}")
        print(f"  - Content-Type: {response_post.headers.get('content-type')}")
        
        # Parse response
        try:
            response_json = response_post.json()
            print(f"  - Response JSON:")
            print(json.dumps(response_json, indent=4, ensure_ascii=False))
        except:
            print(f"  - Response Text: {response_post.text[:500]}")
        
        # === PHÂN TÍCH LỖI ===
        print("\n" + "="*60)
        print("📊 PHÂN TÍCH KẾT QUẢ")
        print("="*60)
        
        if response_post.status_code == 200:
            print("✅ Request thành công!")
        elif response_post.status_code == 400:
            print("❌ Lỗi 400 - Bad Request")
            print("Nguyên nhân có thể:")
            print("  - Thiếu trường bắt buộc trong body")
            print("  - Sai định dạng số điện thoại")
            print("  - Thiếu cookies/session")
        elif response_post.status_code == 401:
            print("❌ Lỗi 401 - Unauthorized")
            print("Nguyên nhân: Thiếu hoặc sai token/session")
        elif response_post.status_code == 422:
            print("❌ Lỗi 422 - Unprocessable Entity")
            print("Nguyên nhân: Dữ liệu không hợp lệ")
        elif response_post.status_code == 429:
            print("❌ Lỗi 429 - Too Many Requests")
            print("Nguyên nhân: Gửi quá nhiều request")
        else:
            print(f"❌ Lỗi {response_post.status_code}")
        
        return {
            "success": response_post.status_code == 200,
            "status_code": response_post.status_code,
            "response": response_post.text,
        }
        
    except requests.exceptions.Timeout:
        print("\n❌ LỖI: Request timeout (quá 15s)")
        return {"error": "timeout"}
    except requests.exceptions.ConnectionError:
        print("\n❌ LỖI: Không thể kết nối đến server")
        return {"error": "connection_error"}
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        return {"error": str(e)}


def test_different_channels(phone):
    channels = ["sms", "ivr", "call", "zalo"]
    
    print("\n" + "="*60)
    print("🧪 TEST VỚI CÁC CHANNEL KHÁC NHAU")
    print("="*60)
    
    for channel in channels:
        print(f"\n--- Testing channel: {channel} ---")
        time.sleep(2)  # Chờ 2s giữa các request

import sys
import time

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python nat1_updated.py <phone_number> <number_of_times>")
        print("Ví dụ: python nat1_updated.py 0123456789 5")
        sys.exit(1)

    phone_number = sys.argv[1]
    number_of_times = int(sys.argv[2])

    print("Phone:", phone_number)
    print(f"Số lần gửi: {number_of_times}")
    print(f"Khoảng cách: Tăng dần 60s, 120s, 180s,...")
    print("="*60)
    
    for i in range(number_of_times):
        print(f"\n🔄 LẦN {i+1}/{number_of_times}")
        print(f"⏰ Thời gian: {datetime.now().strftime('%H:%M:%S')}")
        
        result = debug_request(phone_number)
        
        print("\n" + "="*60)
        print(f"🏁 KẾT QUẢ LẦN {i+1}")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Chờ tăng dần: lần 1 chờ 60s, lần 2 chờ 120s, lần 3 chờ 180s,...
        if i < number_of_times - 1:
            wait_time = (i + 1) * 60  # 60, 120, 180, 240,...
            print(f"\n⏳ Chờ {wait_time} giây ({wait_time//60} phút) trước lần tiếp theo...")
            time.sleep(wait_time)
    
    print("\n" + "="*60)
    print("✅ HOÀN THÀNH TẤT CẢ CÁC LẦN GỬI")
    print("="*60)
