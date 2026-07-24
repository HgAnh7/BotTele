import sys
import requests

# phone = input('SĐT: ')
phone = sys.argv[1]
good = '\033[92m[✓] Thành công\033[0m '
bad = '\033[91m[✗] Thất bại\033[0m '

def vayxanh(phone):
	session = requests.Session()
	session.get(
		f"https://lk.vayxanh.com/?phone={phone}&utm_source=direct_vayxanh",
		timeout=10
	)

	cabinet_key = session.cookies.get("_cabinet_key")
	if not cabinet_key:
		return print(bad + '[VayXanh]')

	response = session.post(
		'https://lk.vayxanh.com/internal/client/otp/send',
		json={'data': {'phone': phone}},
		timeout=10
	)

	if 'data' in response.json():
		print(good + '[VayXanh]')
	else:
		print(bad + '[VayXanh]')
		print(response.json())

vayxanh(phone)
