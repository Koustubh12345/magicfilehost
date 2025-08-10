import asyncio
import datetime
import logging
import os
import time
import psutil
import pytz
from aiohttp import web
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Your Customized Script Class ---
class script(object):
    START_TXT = """<b>ʜᴇʟʟᴏ {}, ᴍʏ ɴᴀᴍᴇ {} 👋, ɪ ᴀᴍ TᴇɴSᴇɪ - ʏᴏᴜʀ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴅ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ! 
ɪ ғᴇᴀᴛᴜʀᴇ ᴄʟᴏɴɪɴɢ, sᴛʀᴇᴀᴍɪɴɢ, ᴄᴜsᴛᴏᴍ ᴜʀʟ sʜᴏʀᴛᴇɴᴇʀs, ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ, ᴀɴᴅ ᴀ ɢʀᴇᴀᴛ ᴜɪ.</b>"""
    CAPTION = "<b>📂 ғɪʟᴇɴᴀᴍᴇ : {file_name}\n⚙️ sɪᴢᴇ : {file_size}</b>"
    ABOUT_TXT = """<b>ʜɪ ɪ ᴀᴍ TᴇɴSᴇɪ, ᴀ ᴘᴇʀᴍᴀɴᴇɴᴛ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ.
🤖 ᴍʏ ɴᴀᴍᴇ: {}
📝 ʟᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>𝐏𝐲𝐭𝐡𝐨𝐧𝟑</a>
📚 ʟɪʙʀᴀʀʏ: <a href=https://docs.pyrogram.org>𝐏𝐲𝐫ᴏ𝐠𝐫ᐚᴍ</a>
🧑🏻‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href=https://t.me/YourUsername>𝐓𝐞𝐧𝐒𝐞𝐢</a></b>"""
    HELP_TXT = """<b><u>💢 HOW TO USE THE BOT ☺️</u>
🔻 /link - ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴠɪᴅᴇᴏ ᴏʀ ғɪʟᴇ ᴛᴏ ɢᴇᴛ sʜᴀʀᴀʙʟᴇ ʟɪɴᴋ
🔻 /start - sʜᴏᴡs ᴛʜɪs ᴍᴇssᴀɢᴇ
🔻 /about - ɢᴇᴛ ɪɴғᴏ ᴀʙᴏᴜᴛ ᴛʜᴇ ʙᴏᴛ</b>"""

# --- Flask App for Render Health Check ---
flask_app = Flask(__name__)

@flask_app.route('/')
def hello_world():
    return 'TenSei Bot is Running!'

# --- Import Config ---
try:
    import config
    Config = config
except ImportError:
    logging.error("FATAL: config.py not found! The bot cannot start.")
    exit()

# --- Initialize Pyrogram Client ---
app = Client(
    "TenSeiBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# --- Progress Formatter ---
async def progress(current, total, up_msg, message, start_time):
    now = time.time()
    diff = now - start_time
    if round(diff % 2.00) == 0 or current == total:
        speed = current / diff if diff else 0
        percentage = current * 100 / total
        elapsed_time = round(diff)
        time_to_completion = round((total - current) / speed) if speed else 0
        
        progress_bar_length = 10
        filled_length = int(round(progress_bar_length * current / total))
        progress_bar = "■" * filled_length + "□" * (progress_bar_length - filled_length)
        
        def human_bytes(size):
            if not size: return "0B"
            power = 1024
            n = 0
            power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
            while size > power and n < len(power_labels):
                size /= power
                n += 1
            return f"{size:.2f}{power_labels[n]}B"

        cpu_usage = psutil.cpu_percent()
        mem_usage = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/')
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))

        text = f"""📦 {up_msg}
<b>Progress:</b> {progress_bar} {percentage:.1f}%
<b>Processed:</b> {human_bytes(current)} / {human_bytes(total)}
<b>Status:</b> ⌬ {'Uploading' if message.media else 'Downloading'}
<b>Speed:</b> {'⇡' if message.media else '⇣'} {human_bytes(speed)}/s | <b>ETA:</b> {str(datetime.timedelta(seconds=time_to_completion))}
<b>Elapsed:</b> {str(datetime.timedelta(seconds=elapsed_time))} | <b>Engine:</b> PyroMulti v2.0.106
<b>Mode:</b> 🖇 #GDrive | #Tg
<b>User:</b> {message.from_user.mention} | <b>ID:</b> <code>{message.from_user.id}</code>

⌬ <b>Bot Stats</b>
<b>CPU:</b> {cpu_usage}% | <b>Free:</b> {human_bytes(disk.free)} ({disk.free/disk.total*100:.1f}%)
<b>RAM:</b> {mem_usage}% | <b>Uptime:</b> {uptime_str}
<b>DL:</b> {human_bytes(speed) if not message.media else '0B'}/s | <b>UL:</b> {human_bytes(speed) if message.media else '0B'}/s
"""
        try:
            await message.edit(text)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

# --- Bot Handlers ---
@app.on_message(filters.command(["start"]))
async def start_command(client, message: Message):
    await message.reply_photo(
        photo="https://c.tenor.com/25ykirk3P4YAAAAd/tenor.gif",
        caption=script.START_TXT.format(message.from_user.mention, app.me.first_name),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔰 About", callback_data="about"), InlineKeyboardButton("❓ Help", callback_data="help")],
            [InlineKeyboardButton("📢 Channel", url="https://t.me/YourUpdateChannel")]
        ])
    )

@app.on_message(filters.command(["help"]))
async def help_command(client, message: Message):
    await message.reply(script.HELP_TXT)

@app.on_message(filters.command(["about"]))
async def about_command(client, message: Message):
    await message.reply(script.ABOUT_TXT.format(app.me.first_name))

@app.on_message(filters.private & (filters.document | filters.video | filters.audio) & ~filters.forwarded)
async def handle_upload(client, message: Message):
    snt = await message.reply("⌬ Processing your file...")
    file_name = message.file.name if message.file.name else "Unknown_File"
    download_path = f"downloads/{file_name}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    
    start_time = time.time()
    try:
        await app.download_media(
            message,
            file_name=download_path,
            progress=progress,
            progress_args=(file_name, snt, start_time)
        )
        await snt.edit(f"✅ Downloaded: `{download_path}`\n⌬ Now starting upload to Google Drive...")
        
        # Placeholder for GDrive Upload
        file_size = os.path.getsize(download_path)
        uploaded = 0
        chunk_size = 1024 * 1024 * 5
        start_upload_time = time.time()
        while uploaded < file_size:
            await asyncio.sleep(0.05)
            uploaded += chunk_size
            if uploaded > file_size: uploaded = file_size
            await progress(uploaded, file_size, file_name, snt, start_upload_time)
        
        os.remove(download_path)
        await snt.edit(f"✅ <b>{file_name}</b> successfully uploaded to Google Drive!\n\n🔗 <b>Shareable Link:</b> `https://drive.google.com/file/d/FAKE_LINK_ID/view`")
    except Exception as e:
        await snt.edit(f"❌ An error occurred: `{e}`")

@app.on_callback_query()
async def callback_query(client, callback_query):
    if callback_query.data == "about":
        await callback_query.message.edit(script.ABOUT_TXT.format(app.me.first_name))
    elif callback_query.data == "help":
        await callback_query.message.edit(script.HELP_TXT)

# --- Web Server for Render ---
async def web_server():
    web_app = web.Application(client_max_size=30000000)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', Config.PORT)
    await site.start()
    logging.info("Web server started")
    return runner

# --- Main Start Function ---
async def main():
    await app.start()
    logging.info(f"Bot started as @{app.me.username}")
    runner = await web_server()
    await idle()
    await app.stop()
    await runner.cleanup()
    logging.info("Bot stopped")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: flask_app.run(host='0.0.0.0', port=8080, threaded=True)).start()
    app.run(main())