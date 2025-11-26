#!/usr/bin/env python3
import os
import requests

token = os.environ.get('TELEGRAM_TOKEN')
chat_id = os.environ.get('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    print('TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set in environment')
    raise SystemExit(1)

resp = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': chat_id, 'text': 'Test desde GitHub Actions: monitor funcionando ✅'})
print(resp.status_code, resp.text)
if resp.status_code != 200:
    raise SystemExit(2)
