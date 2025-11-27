# Monitor price+deals watcher (Telegram)

This small project runs in GitHub Actions (cloud) and checks product pages and category pages for changes, price drops and new posts that match keywords.

It is configured to watch: PcComponentes, Amazon and Chollometro 'monitores' section (customizable). When something interesting is detected it sends a Telegram message to your chat.

Features
- Poll pages every X minutes (GitHub Actions cron). Default configured for every 15 minutes.
- Look for price thresholds, keyword matches or new posts on sections (Chollometro)
- Persist seen items in state.json and commit changes back to the repo so it won't repeat notifications.

Quick deployment
1. Create a GitHub repository and push files from this folder.
2. In your GitHub repo, create two secrets: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID
3. Enable Actions and the scheduled workflow will run automatically.

If you prefer, I can upload these files to a public repo for you — say the repo name and whether you want it public or private.


Customization
- Edit `config.json` to add/remove URLs and keywords.
- Edit `FREQUENCY_MINUTES` in `.github/workflows/monitor.yml` if you want a different frequency.

Requirements
- Python 3.10+ (used in the Actions workflow)

License: MIT

Local testing
--------------

1. Install Python dependencies (preferably in a virtualenv):

	```bash
	python -m venv .venv
	source .venv/bin/activate
	pip install -r monitor/requirements.txt
	```

2. Set Telegram credentials in environment variables, or pass them via CLI args when testing:

	```bash
	export TELEGRAM_TOKEN="<your bot token>"
	export TELEGRAM_CHAT_ID="<your chat id>"
	```

3. Run a quick telegram test (safe to run; will send an actual message if token is valid):

	```bash
	python monitor/test_send.py
	# or override via CLI
	python monitor/test_send.py --token 123:abc --chat-id 987654
	```

4. Run the monitor script in dry-run mode (so it won't send messages):

	```bash
	python monitor/monitor.py --dry-run
	# or pass telegram token/chat id via CLI
	python monitor/monitor.py --dry-run --telegram-token 123:abc --telegram-chat-id 987654
	```

Notes
- If you run `python monitor/monitor.py` from the repository root the script will still find `monitor/config.json` and `monitor/state.json` automatically.
- If you want to run the script from a different location, use `--config` and `--state` to point to those files.
 - You can also store your credentials in an `.env` file in the `monitor/` folder (recommended for local development).
	 1. Copy `monitor/.env.example` to `monitor/.env` and fill in `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`.
	 2. The repo `.gitignore` already ignores `monitor/.env` to avoid committing secrets.
