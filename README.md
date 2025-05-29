# Hausa Escrow Bot 🤖

A simple Telegram bot for handling basic escrow transactions in Hausa language.

## Files Included
- `main.py`: Main bot logic.
- `.env.example`: Rename to `.env` and provide your secrets.
- `.gitignore`: Prevents uploading secrets and cache.
- `README.md`: You are here!

## Running the Bot

1. Create a `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Fill in your bot token and IDs inside `.env`.

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```bash
   python main.py
   ```

Make sure `.env` is never uploaded to GitHub to keep your token secret.
