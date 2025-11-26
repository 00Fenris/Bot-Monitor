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
