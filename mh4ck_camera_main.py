import threading
import time
from bot_telegram import main as run_bot
from web_server import run_flask

def run_web_server():
    """Run Flask web server"""
    print("Starting Flask web server...")
    run_flask()

def run_telegram_bot():
    """Run Telegram bot"""
    print("Starting Telegram bot...")
    time.sleep(1) 
    run_bot()

if __name__ == "__main__":
    print("Starting Tracking Link System...")
    
    web_thread = threading.Thread(target=run_web_server)  
    web_thread.daemon = True  
    web_thread.start()
    
    print("Waiting for web server to start...")
    time.sleep(5)  
    
    run_telegram_bot()