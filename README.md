# 🤖 Hausa Escrow Bot (Termux Edition)

Wannan bot yana taimaka wa masu siye da sayarwa su yi cinikayya cikin aminci ta hanyar escrow a Telegram.

## 🧰 Abubuwan da ake bukata
- Android phone
- Termux app
- Python 3

## 🛠 Matakan girkawa a Termux
```bash
pkg update && pkg upgrade -y
pkg install python git unzip -y
pip install -r requirements.txt
```

## 📁 Abubuwan da ke cikin wannan project:
- `main.py` – Babban code na bot
- `.env` – Domin saka BOT_TOKEN da ADMIN_ID
- `requirements.txt` – Libraries da ake buƙata
- `README.md` – Wannan bayanin
- `.gitignore` – Don hana sakawa `.env` a GitHub

## 🚀 Gudanar da bot
```bash
python main.py
```

## 🔄 24/7 Gudana (ta amfani da tmux)
```bash
pkg install tmux
tmux
python main.py
```
> Don fita daga tmux: CTRL + B, sai D

## 🤝 Contact
Admin: Bashir Rabiu  
Telegram Bot: @HausaEscrowBot  
Wallet TRC20: TRjqMH6ckyNVaCBXNDkKitq1phCV1YSugg  
Naira Account: Opay 9131085651 - Bashir Rabiu