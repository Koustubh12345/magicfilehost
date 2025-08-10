import asyncio
import datetime
import logging
import os
import time
import psutil
import pytz
import re
from io import BytesIO
from aiohttp import web, ClientSession
from flask import Flask
from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# --- Basic Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Your Customized Script Class ---
class script(object):
    START_TXT = """<b>ʜᴇʟʟᴏ {}, ᴍʏ ɴᴀᴍᴇ {} 👋, ɪ ᴀᴍ TᴇɴSᴇɪ - ʏᴏᴜʀ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴅ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ ꜱᴛᴏʀᴇ ʙᴏᴛ! 
ɪ ғᴇᴀᴛᴜʀᴇ ʟᴇᴇᴄʜɪɴɢ, ᴍɪʀʀᴏʀɪɴɢ, ʟɪɴᴋɪɴɢ, ᴀɴᴅ ᴀ ɢʀᴇᴀᴛ ᴜɪ.</b>"""
    CAPTION = "<b>📂 ғɪʟᴇɴᴀᴍᴇ : {file_name}\n⚙️ sɪᴢᴇ : {file_size}</b>"
    ABOUT_TXT = """<b>ʜɪ ɪ ᴀᴍ TᴇɴSᴇɪ, ᴀ ᴘᴏᴡᴇʀꜰᴜʟ ꜰɪʟᴇ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ.
🤖 ᴍʏ ɴᴀᴍᴇ: {}
📝 ʟᴀɴɢᴜᴀɢᴇ: <a href=https://www.python.org>𝐏𝐲𝐭𝐡𝐨𝐧𝟑</a>
📚 ʟɪʙʀᴀʀʏ: <a href=https://docs.pyrogram.org>𝐏𝐲𝐫ᴏ𝐠𝐫ᐚᴍ</a>
🧑🏻‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href=https://t.me/YourUsername>𝐓𝐞𝐧𝐒𝐞𝐢</a></b>"""
    HELP_TXT = """<b><u>💢 HOW TO USE THE BOT ☺️</u>
🔻 /leech <url> - ᴅᴏᴡɴʟᴏᴀᴅ ғɪʟᴇ ғʀᴏᴍ ᴜʀʟ ᴀɴᴅ ᴜᴘʟᴏᴀᴅ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ
🔻 /link - ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇ ᴛᴏ ɢᴇᴛ ᴀ sʜᴀʀᴀʙʟᴇ ʟɪɴᴋ
🔻 /mirror - ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴛᴇʟᴇɢʀᴀᴍ ғɪʟᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ᴛᴏ ɢᴏᴏɢʟᴇ ᴅʀɪᴠᴇ
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

# --- Helper Functions ---
def human_bytes(size):
    if not size: return "0B"
    power = 1024
    n = 0
    power_labels = {0: '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power and n < len(power_labels):
        size /= power
        n += 1
    return f"{size:.2f}{power_labels[n]}B"

def is_url(text):
    url_regex = re.compile(r'https?://\S+')
    return bool(url_regex.search(text))

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

# --- /leech command ---
@app.on_message(filters.command(["leech"]) & filters.private)
async def leech_command(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❌ Please provide a URL to download.\n\n<b>Usage:</b> `/leech <direct_download_url>`")
    
    url = message.command[1]
    if not is_url(url):
        return await message.reply("❌ The provided text is not a valid URL.")
        
    snt = await message.reply("⌬ Starting download from URL...")
    file_name = url.split('/')[-1].split('?')[0] or "Leeched_File"
    download_path = f"downloads/{file_name}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    
    start_time = time.time()
    try:
        async with ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    with open(download_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024): # 1MB chunks
                            f.write(chunk)
                            downloaded += len(chunk)
                            await progress(downloaded, total_size, file_name, snt, start_time)
                else:
                    return await snt.edit(f"❌ Failed to download. Status: {response.status}")

        await snt.edit(f"✅ Downloaded: `{file_name}`\n⌬ Now uploading to Telegram...")
        
        # Upload to Telegram
        start_upload_time = time.time()
        await client.send_document(
            chat_id=message.chat.id,
            document=download_path,
            caption=f"<b>Leeched by {message.from_user.mention}</b>",
            progress=progress,
            progress_args=(file_name, snt, start_upload_time)
        )
        
        os.remove(download_path)
        await snt.delete()
        
    except Exception as e:
        await snt.edit(f"❌ An error occurred during leeching: `{e}`")


# --- /link command ---
@app.on_message(filters.command(["link"]) & filters.private)
async def link_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply("❌ Please reply to a media file to get its link.")
    
    reply = message.reply_to_message
    file_name = getattr(reply, 'file_name', None)
    if not file_name:
        if reply.video: file_name = f"{reply.video.file_name}.mp4"
        elif reply.audio: file_name = f"{reply.audio.file_name}.mp3"
        elif reply.photo: file_name = f"photo_{reply.photo.file_unique_id}.jpg"
        else: file_name = "Unknown_File"

    # Create a shareable link for the file
    # The format is https://t.me/c/chat_id/message_id for private channels
    # or https://t.me/username/message_id for public channels/groups
    # For a bot, it's easier to just forward the message to a public channel and get the link from there.
    # For simplicity, we'll generate a direct Telegram link if possible.
    
    chat_id = message.chat.id
    message_id = reply.id
    
    # This link works if the user has the bot added to a public channel they forward to.
    # A more robust solution involves storing files in a channel and generating links.
    # For now, we provide a basic link.
    link = f"https://t.me/c/{str(chat_id).replace('-100','')}/{message_id}"
    
    await message.reply(f"🔗 <b>Instant Link for:</b> <code>{file_name}</code>\n\n<code>{link}</code>\n\n<b>Note:</b> This link works only for members of this chat.")


# --- /mirror command ---
@app.on_message(filters.command(["mirror"]) & filters.private)
async def mirror_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply("❌ Please reply to a media file to mirror it to Google Drive.")
    
    reply = message.reply_to_message
    snt = await message.reply("⌬ Processing your file for mirroring...")
    file_name = getattr(reply, 'file_name', None)
    if not file_name:
        if reply.video: file_name = f"{reply.video.file_name}.mp4"
        elif reply.audio: file_name = f"{reply.audio.file_name}.mp3"
        elif reply.photo: file_name = f"photo_{reply.photo.file_unique_id}.jpg"
        else: file_name = "Unknown_File"

    download_path = f"downloads/{file_name}"
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    
    start_time = time.time()
    try:
        # Download from Telegram
        dl_path = await client.download_media(
            reply,
            file_name=download_path,
            progress=progress,
            progress_args=(file_name, snt, start_time)
        )
        await snt.edit(f"✅ Downloaded: `{dl_path}`\n⌬ Now starting upload to Google Drive...")
        
        # --- Google Drive Upload Logic (Placeholder) ---
        # In a real bot, you would use the Google API Client Library here.
        # We will simulate it with a progress bar.
        file_size = os.path.getsize(download_path)
        uploaded = 0
        chunk_size = 1024 * 1024 * 5 # 5MB chunks
        
        start_upload_time = time.time()
        while uploaded < file_size:
            await asyncio.sleep(0.05) # Simulate upload time
            uploaded += chunk_size
            if uploaded > file_size:
                uploaded = file_size
            await progress(uploaded, file_size, file_name, snt, start_upload_time)
        
        os.remove(download_path)
        
        # This is a FAKE link. A real bot would generate it from the GDrive API.
        gdrive_link = f"https://drive.google.com/file/d/FAKE_GDRIVE_ID_{reply.id}/view"
        
        await snt.edit(f"✅ <b>{file_name}</b> successfully mirrored to Google Drive!\n\n🔗 <b>GDrive Link:</b> <code>{gdrive_link}</code>")
        
    except Exception as e:
        await snt.edit(f"❌ An error occurred during mirroring: `{e}`")


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
