# Suggestion Telegram Bot

- for **forwarding messages** created for [Half-Life Collective](https://t.me/HalfLifeCollective)
- Bot link **(Telegram)**: [@hl_suggestion_bot](https://t.me/hl_suggestion_bot)

Developers:
- [Elinsrc](https://github.com/Elinsrc)
- [w_sh1t](https://github.com/wh1tesh1t)

## How to install?

## Linux
```shell
apt install python3
git clone https://github.com/Elinsrc/Suggestion
```

```shell
pip3 install -r requirements.txt
cp -r config.py.example config.py
nano config.py
```

After replace all necessary values in config.py with your own:
```Example Config
TOKEN: str = "123456789:qwertyuiopasdfghjklkzxcvbnm"
API_ID: int = 123456789
API_HASH: str = "1q2w3e4r5t6y7u8i9o0p"
DATABASE_PATH = "bot.db"
WORKERS = 24
FORWARDING_CHAT = 123456789
```

Run the bot:
```shell
pythom3 -m bot
```

Have fun!
