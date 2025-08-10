import os

# --- REQUIRED: Bot Information ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "TenSeiBot")

# --- REQUIRED: Google Drive API Credentials ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID", "")

# --- REQUIRED: Admins ---
ADMINS = [int(admin) for admin in os.environ.get('ADMINS', '0').split()]

# --- Server Configuration ---
PORT = int(os.environ.get("PORT", "8080"))