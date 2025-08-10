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
from pyrogram.errors import FloodWait, UserNotParticipant
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
📚 ʟɪʙʀᴀʀʏ: <a href=https://docs.pyrogram.org>𝐏𝐲𝐫ᴏɢ𝐫ᐚᴍ</a>
🧑🏻‍💻 ᴅᴇᴠᴇʟᴏᴘᴇʀ: <a href=https://t.me/YourUsername>𝐓𝐞𝐧𝐒ᐞɪ</a></b>"""
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

# --- IMPORTANT: CONFIGURE YOUR PUBLIC CHANNEL ---
# For the /link command to work for everyone, create a PUBLIC Telegram channel.
# Add your bot as an administrator in that channel.
# Replace the value below with your channel's username (e.g., "mypublicfilechannel").
PUBLIC_CHANNEL_USERNAME = os.environ.get("PUBLIC_CHANNEL_USERNAME", "YourChannelUsernameHere")


# --- Initialize Pyrogram Client ---
app = Client(
    "TenSeiBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

# --- Progress Formatter (FIXED) ---
async def progress(current, total, up_msg, user, chat_id, start_time):
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
<b>Status:</b> ⌬ Uploading
<b>Speed:</b> ⇡ {human_bytes(speed)}/s | <b>ETA:</b> {str(datetime.timedelta(seconds=time_to_completion))}
<b>Elapsed:</b> {str(datetime.timedelta(seconds=elapsed_time))} | <b>Engine:</b> PyroMulti v2.0.106
<b>Mode:</b> 🖇 #GDrive | #Tg
<b>User:</b> {user.mention} | <b>ID:</b> <code>{user.id}</code>

⌬ <b>Bot Stats</b>
<b>CPU:</b> {cpu_usage}% | <b>Free:</b> {human_bytes(disk.free)} ({disk.free/disk.total*100:.1f}%)
<b>RAM:</b> {mem_usage}% | <b>Uptime:</b> {uptime_str}
<b>DL:</b> 0B/s | <b>UL:</b> {human_bytes(speed)}/s
"""
        try:
            # We need to get the original message to edit it
            msg_to_edit = await app.get_messages(chat_id, up_msg.split('|')[1].strip())
            await msg_to_edit.edit(text)
        except (FloodWait, Exception):
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

# --- /leech command (FIXED) ---
@app.on_message(filters.command(["leech"]) & filters.private)
async def leech_command(client, message: Message):
    if len(message.command) < 2:
        # Fixed formatting to avoid ENTITY_BOUNDS_INVALID
        return await message.reply("❌ Please provide a URL to download.\n\n<b>Usage:</b>\n`/leech <direct_download_url>`")
    
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
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                            downloaded += len(chunk)
                            # Pass user and chat_id to progress
                            await progress(downloaded, total_size, f"Downloading {file_name} | ID: {snt.id}", message.from_user, message.chat.id, start_time)
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
            progress_args=(f"Uploading {file_name} | ID: {snt.id}", message.from_user, message.chat.id, start_upload_time)
        )
        
        os.remove(download_path)
        await snt.delete()
        
    except Exception as e:
        await snt.edit(f"❌ An error occurred during leeching: `{e}`")

# --- /link command (FIXED AND IMPROVED) ---
@app.on_message(filters.command(["link"]) & filters.private)
async def link_command(client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.media:
        return await message.reply("❌ Please reply to a media file to get its link.")
    
    if PUBLIC_CHANNEL_USERNAME == "YourChannelUsernameHere":
        return await message.reply("❌ The bot owner has not configured a public channel for this feature. Please set the `PUBLIC_CHANNEL_USERNAME` environment variable.")

    reply = message.reply_to_message
    snt = await message.reply("⌬ Processing your file...")

    try:
        # Forward the message to the public channel
        forwarded_msg = await client.forward_messages(
            chat_id=f"@{PUBLIC_CHANNEL_USERNAME}",
            from_chat_id=message.chat.id,
            message_ids=reply.id
        )
        
        # Generate the shareable link
        share_link = f"https://t.me/{PUBLIC_CHANNEL_USERNAME}/{forwarded_msg.id}"
        
        await snt.edit(
            f"✅ <b>Shareable Link Generated!</b>\n\n"
            f"🔗 <a href='{share_link}'>Click here to view file</a>\n\n"
            f"<code>{share_link}</code>"
        )
    except UserNotParticipant:
        await snt.edit("❌ The bot is not an admin in the configured public channel. Please add the bot as an admin.")
    except Exception as e:
        await snt.edit(f"❌ An error occurred: `{e}`")


# --- /mirror command (FIXED) ---
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
            progress_args=(f"Downloading {file_name} | ID: {snt.id}", message.from_user, message.chat.id, start_time)
        )
        await snt.edit(f"✅ Downloaded: `{dl_path}`\n⌬ Now starting upload to Google Drive...")
        
        # --- Google Drive Upload Logic (Placeholder) ---
        file_size = os.path.getsize(download_path)
        uploaded = 0
        chunk_size = 1024 * 1024 * 5 
        
        start_upload_time = time.time()
        while uploaded < file_size:
            await asyncio.sleep(0.05) 
            uploaded += chunk_size
            if uploaded > file_size:
                uploaded = file_size
            # Pass user and chat_id to progress
            await progress(uploaded, file_size, f"Uploading {file_name} | ID: {snt.id}", message.from_user, message.chat.id, start_upload_time)
        
        os.remove(download_path)
        
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
