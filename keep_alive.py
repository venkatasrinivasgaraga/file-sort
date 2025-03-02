from flask import Flask
import threading

app = Flask(_name_)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def start_keep_alive():
    thread = threading.Thread(target=run_flask)
    thread.daemon = True
    thread.start()
