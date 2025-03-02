import os
import re
import hashlib
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from keep_alive import start_keep_alive  # Import keep-alive function

# Replace with your Telegram bot token
BOT_TOKEN = "your_bot_token_here"

# Folder to store files
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Function to get file hash (for duplicate detection)
def get_file_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

# Extract file number from filename (e.g., "0001_document.pdf" → 1)
def extract_file_number(filename):
    match = re.search(r"(\d+)", filename)
    return int(match.group(1)) if match else float('inf')

# Start command
async def start(update: Update, context):
    await update.message.reply_text("Send me files, and I'll sort them by number and remove duplicates.")

# Handle incoming files
async def handle_document(update: Update, context):
    file = update.message.document
    file_name = file.file_name
    file_path = os.path.join(DOWNLOAD_FOLDER, file_name)

    # Download file
    file_obj = await file.get_file()
    await file_obj.download_to_drive(file_path)

    # Check for duplicates
    file_hash = get_file_hash(file_path)
    for existing_file in os.listdir(DOWNLOAD_FOLDER):
        existing_path = os.path.join(DOWNLOAD_FOLDER, existing_file)
        if existing_path != file_path and get_file_hash(existing_path) == file_hash:
            os.remove(file_path)  # Remove duplicate
            await update.message.reply_text(f"❌ Duplicate file removed: {file_name}")
            return

    await update.message.reply_text(f"✅ File received: {file_name}")

# Command to sort files
async def sort_files(update: Update, context):
    files = os.listdir(DOWNLOAD_FOLDER)
    sorted_files = sorted(files, key=extract_file_number)

    sorted_list = "\n".join(sorted_files)
    await update.message.reply_text(f"📂 Sorted files:\n{sorted_list}")

# Set up the bot
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("sort", sort_files))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot is running...")
    app.run_polling()

if _name_ == "_main_":
    start_keep_alive()  # Start the keep-alive server
    main()  # Start the Telegram bot
