#!/usr/bin/env python3
import os
import argparse
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

parser = argparse.ArgumentParser()
parser.add_argument('--token', help='Telegram bot token (overrides TELEGRAM_TOKEN env var)')
parser.add_argument('--chat-id', help='Telegram chat id (overrides TELEGRAM_CHAT_ID env var)')
args = parser.parse_args()

token = args.token or os.environ.get('TELEGRAM_TOKEN')
chat_id = args.chat_id or os.environ.get('TELEGRAM_CHAT_ID')

if not token or not chat_id:
    print('TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set in environment or CLI arguments')
    raise SystemExit(1)

resp = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', data={'chat_id': chat_id, 'text': 'Test desde GitHub Actions: monitor funcionando ✅'})
print(resp.status_code, resp.text)
if resp.status_code != 200:
    raise SystemExit(2)
