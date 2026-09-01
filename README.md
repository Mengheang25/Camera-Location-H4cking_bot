# 📸 M.h4ck Camera – Tracking Telegram Bot

This project is a **Tracking Telegram Bot** that demonstrates how a Telegram bot and a Flask web server can be used together to generate tracking links and collect device information when someone visits those links. The collected data (device info, location, camera photos, IP, etc.) is posted back to the server and forwarded to the link creator via Telegram notifications.

> **Important:** This tool is capable of collecting highly sensitive personal data (location, photos, IP address). Using it to collect data from people without their explicit consent is likely illegal and unethical. Use this project only for learning, authorized penetration testing, or other legitimate, consented scenarios.

---

## ✅ What’s included in this project
- A Telegram bot (using `python-telegram-bot`) to accept commands, create tracking links, and send notifications.
- A Flask web server that serves a tracking page (HTML + JS) which collects device information and camera photos.
- Integration with `pyngrok` to expose a local Flask server over HTTPS with a public URL.
- Image processing with `Pillow` to add a watermark and save captured images locally.
- Simple in-memory shared data module (`shared_data.py`) used by both bot and web server.

---

## ⚙️ Requirements (packages & versions)
Add this `requirements.txt` to the project root (recommended):

```
--only-binary :all:
aiogram==3.17.0
Flask==3.0.3
pyngrok==7.1.4
Pillow==11.0.0
requests==2.32.3
python-telegram-bot==21.10
urllib3==2.3.0
Werkzeug==3.0.3
```

> Note: The `--only-binary :all:` line tells `pip` to prefer pre-built wheels. If you encounter wheel/build errors, remove that line and try again.

---

## 🧰 Installation (local development)
Run the following on Linux/macOS or Windows (WSL recommended):

1. **Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

2. **Create `requirements.txt`**
Place the packages listed above into a file named `requirements.txt` in your project root.

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install aiogram Flask pyngrok Pillow requests python-telegram-bot
pip install -r requirements.txt
```

If you see errors about building wheels or missing compilers, remove the `--only-binary :all:` line from `requirements.txt` and retry.

---

## 🔧 Required environment variables
Create a `.env` file or export these variables before running the services:

- `TELEGRAM_BOT_TOKEN` — Your bot token from BotFather.
- `NGROK_AUTHTOKEN` — authtoken API from ngrok.

Example `.env`:

```
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN_HERE
```

**Security note:** Keep your bot token secret. Never commit it to a public repository.

---

## ▶️ How to run
You can run the web server and bot in separate terminals or use a launcher script that starts the Flask server in a background thread and the bot in the main thread.

**Option A — Run separately**

Terminal 1 (web server):

```bash
# POSIX example
export TELEGRAM_BOT_TOKEN="<token>"
export NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN_HERE
python web_server.py
```

Terminal 2 (bot):

```bash
export TELEGRAM_BOT_TOKEN="<token>"
export BOT_PASSWORD="<password>"
python bot.py
```

**Option B — Single launcher**
If you have `launcher.py` (a small script that starts Flask in a thread and runs the bot in the main thread):

```bash
export TELEGRAM_BOT_TOKEN="<token>"
export NGROK_AUTHTOKEN=YOUR_NGROK_AUTH_TOKEN_HERE
python launcher.py
```

---

## 🌐 Ngrok (optional)
If you want to expose a local Flask server to the public internet over HTTPS, use ngrok.

1. Install ngrok and sign in to get an authtoken.
2. `pyngrok` is used in the code to create tunnels programmatically.

**Note:** Ngrok public URLs can change between sessions unless you have a reserved domain; keep your token private.

---

## 🖼️ Images and storage
- Captured images are saved to `captured_images/` (the server creates the folder if missing).
- A watermark (default: `t.me/mengheang25`) is added to saved images. You can change the watermark text in the server code.

---

## 🛡️ Legal & ethical considerations
- Do **not** use this system to collect data from people without clear, informed consent.
- Use only for authorized testing, research, or educational purposes.
- If deploying in production or organizational environments, obtain legal review and explicit consent forms.

---

## 🧪 Testing & troubleshooting
- **Bot not responding?** Check the bot token, network connectivity, and runtime logs.
- **Ngrok tunnel not created?** Verify your ngrok authtoken and network/firewall settings.
- **getUserMedia failing in browser?** Browser requires HTTPS and explicit permission for camera and location. Use ngrok HTTPS tunnel or host the site over HTTPS.
- **Memory usage high when capturing 15 photos?** Base64 image payloads can be large. Reduce the capture resolution or number of photos if needed.

---

## 🧾 Example project layout
```
project-root/
├─ bot_telegram.py
├─ docker_compose.yaml
├─ web_server.py
├─ shared_data.py
├─ launcher.py        # optional (start both services)
├─ mh4ck_camera_main.py
├─ requirements.txt
├─ captured_images/
├─ .env
├─ ngork.exe
└─ README.md
```
---

## 👤 Developer
Created and maintained by **Meng Heang**  
Telegram: [@mengheang25](https://t.me/mengheang25)
---
