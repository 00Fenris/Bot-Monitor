#!/usr/bin/env python3
import os
import json
import hashlib
import time
import re
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime

from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, '.env'))
STATE_FILE = os.environ.get('MONITOR_STATE', os.path.join(SCRIPT_DIR, 'state.json'))
CONFIG_FILE = os.environ.get('MONITOR_CONFIG', os.path.join(SCRIPT_DIR, 'config.json'))
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117 Safari/537.36'
}


def load_config(path=None):
    if path is None:
        path = CONFIG_FILE
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def load_state(path=None):
    if path is None:
        path = STATE_FILE
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf8') as f:
        return json.load(f)


def save_state(state, path=None):
    if path is None:
        path = STATE_FILE
    with open(path, 'w', encoding='utf8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[ERR] fetch {url}: {e}")
        return None


def text_hash(s):
    return hashlib.sha256(s.encode('utf8')).hexdigest()


def extract_price(text):
    # find something like 1.234,56 € or 123,45 EUR or 123.45
    m = re.search(r"([0-9]{1,3}(?:[\.,][0-9]{3})*(?:[\.,][0-9]{2}))\s*(€|EUR)?", text)
    if not m:
        m = re.search(r"(\d+[\.,]\d{2})", text)
    if not m:
        return None
    val = m.group(1)
    val = val.replace('.', '').replace(',', '.')
    try:
        return float(val)
    except:
        return None


def telegram_send(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print('[WARN] TELEGRAM_TOKEN or TELEGRAM_CHAT_ID not set — skipping telegram')
        return False
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code == 200:
            print('[OK] sent to telegram')
            return True
        else:
            print(f'[ERR] telegram send status={r.status_code} {r.text}')
            return False
    except Exception as e:
        print(f'[ERR] telegram send exception: {e}')
        return False


def check_target(target, state):
    url = target['url']
    name = target.get('name', url)
    content = fetch(url)
    if not content:
        return False

    soup = BeautifulSoup(content, 'lxml')
    # use full text for keyword search
    text = soup.get_text(separator=' ', strip=True)
    found_keywords = [k for k in target.get('keywords', []) if k.lower() in text.lower()]

    # compute a relevant block to hash — for sections, keep first N characters
    if target['type'] == 'section':
        # Focus only on the first 40k chars to avoid extras
        block = text[:40000]
    else:
        block = text

    h = text_hash(block)
    old = state.get(target['id'], {})
    old_h = old.get('hash')

    triggered = False
    messages = []

    # detect new/changed
    if old_h != h:
        triggered = True
        messages.append(f"<b>CAMBIO DETECTADO</b> en <i>{name}</i>\n{url}")

    # price check
    price = extract_price(text)
    threshold = target.get('price_threshold_eur')
    if price is not None and threshold is not None:
        try:
            price_val = float(price)
            if price_val <= threshold:
                triggered = True
                messages.append(f"<b>PRECIO BAJO</b> {price_val} € <= {threshold} € en <i>{name}</i>\n{url}")
        except:
            pass

    # keywords
    if found_keywords:
        triggered = True
        keywords_list = ', '.join(found_keywords[:6])
        messages.append(f"<b>KEYWORDS:</b> {keywords_list} encontrados en <i>{name}</i>\n{url}")

    # update state
    state[target['id']] = {'hash': h, 'last_checked': datetime.utcnow().isoformat(), 'last_price': price}

    # return notifications
    if triggered:
        text_out = '\n\n'.join(messages)
        return text_out
    return None


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='Path to config.json (default: monitor/config.json)')
    parser.add_argument('--state', help='Path to state.json (default: monitor/state.json)')
    parser.add_argument('--dry-run', action='store_true', help='Do not send telegram messages; useful for testing')
    parser.add_argument('--telegram-token', help='Telegram bot token (overrides TELEGRAM_TOKEN env var)')
    parser.add_argument('--telegram-chat-id', help='Telegram chat id (overrides TELEGRAM_CHAT_ID env var)')
    args = parser.parse_args(argv)

    config = load_config(args.config)
    state = load_state(args.state)

    # optionally override telegram vars from CLI for tests
    global TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    if args.telegram_token:
        TELEGRAM_TOKEN = args.telegram_token
    if args.telegram_chat_id:
        TELEGRAM_CHAT_ID = args.telegram_chat_id

    alerts = []
    for t in config.get('targets', []):
        print(f"Checking {t['id']} {t.get('name')} -> {t['url']}")
        msg = check_target(t, state)
        if msg:
            alerts.append(msg)

    if alerts:
        message = '<b>ALERTAS MONITOR</b>\n\n' + '\n\n-----\n\n'.join(alerts)
        if args.dry_run:
            print('[INFO] Dry-run mode: not sending telegram message')
            print(message)
        else:
            telegram_send(message)
        # save state (we will let the workflow commit it back if desired)
        save_state(state, args.state)
        # exit 0 to indicate success
        return 0
    else:
        save_state(state, args.state)
        print('No interesting changes')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
