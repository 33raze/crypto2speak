from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
from threading import Thread
import os

# ── Your Bot Config ──
API_ID = 22550296
API_HASH = "07a81de905abdc7f69ba57412704bb01"
BOT_TOKEN = "8179366580:AAEwO_AdzEid8fYsC9FaE3P92Nuot9TuIug"
LOG_CHANNEL = "@validised"
POST_CHANNEL = "@speakverse"

PRICES = {
    "text": 0.20, "photo": 0.20, "voice": 3.00,
    "video": 0.40, "sticker": 0.50
}

app = Client("shoutout-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ── Helpers ──
def calculate_price(msg: Message):
    if msg.text: return round(len(msg.text) * PRICES["text"], 2), "Text"
    elif msg.photo: return PRICES["photo"], "Image"
    elif msg.voice: return round(msg.voice.duration * PRICES["voice"], 2), "Voice"
    elif msg.video: return round(msg.video.duration * PRICES["video"], 2), "Video"
    elif msg.sticker: return PRICES["sticker"], "Sticker"
    return 0, "Unknown"

def is_valid_txid(text): return len(text) >= 10 and any(char.isdigit() for char in text)

# ── Commands ──
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply(
        "**🎙️ Welcome to the Speak Verse!**\n\n"
        "Send /new to begin submitting a message.\n\n"
        "**💰 Pricing:**\n"
        "- Text: $0.20/character\n- Image: $0.20\n- Voice: $3.00/sec\n"
        "- Video: $0.40/sec\n- Sticker: $0.50"
    )

@app.on_message(filters.command(["pricing", "menu"]))
async def pricing(client, message):
    await message.reply(
        "**💰 Pricing Menu:**\n"
        "- Text: $0.20/char\n- Image: $0.20\n- Voice: $3.00/sec\n"
        "- Video: $0.40/sec\n- Sticker: $0.50\n\n"
        "**📛 Content Policy:**\nWe review all posts before publishing to @speakverse."
    )

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply(
        "**📌 How It Works:**\n"
        "1. /new → Send your message\n2. Get cost\n3. Pay in crypto\n4. Send TXID\n"
        "5. Admin reviews & posts it"
    )

@app.on_message(filters.command("new"))
async def new_message(client, message):
    await message.reply("✍️ Send your message now. I’ll calculate the price.")

# ── Main Handler ──
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "pricing", "menu", "new"]))
async def handle_user_input(client, message):
    txid = message.text.strip()
    if is_valid_txid(txid):
        user = message.from_user
        await message.reply("✅ Received! We’ll review and post it soon.")
        await client.send_message(LOG_CHANNEL, f"💸 TXID from @{user.username or user.first_name}:\n`{txid}`")
    else:
        price, content_type = calculate_price(message)
        if price == 0:
            await message.reply("❌ Not a valid TXID.\nSend /new to start again.")
            return
        await message.reply(
            f"💸 **{content_type} Price:** `${price:.2f}`\n\n"
            "**🔐 Pay to any of these wallets:**\n\n"
            "**• BTC**\n`15oQGcNp4GtUCH4w38wqVziPmaLTzwSHVX`\n\n"
            "**• ETH (ERC20)**\n`0x313dd4d737941146dea8117a706b507c2cfc0147`\n\n"
            "**• USDT (TRC20)**\n`THzmvaDHUUU61uqizyMZfqeTQHpgodL9ym`\n\n"
            "**• BNB (BEP20)**\n`0x313dd4d737941146dea8117a706b507c2cfc0147`\n\n"
            "**• SOL**\n`95v6HNk4yz6hngmRYm16DsUqnkGZQM3y5rWQ796szma8`\n\n"
            "📨 After paying, send your TXID here.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📨 Contact Admin", url="https://t.me/validising")]
            ])
        )
        await client.send_message(LOG_CHANNEL, f"👤 New {content_type} - ${price:.2f} from @{message.from_user.username or message.from_user.first_name}")
        await message.copy(LOG_CHANNEL)

# ── Uptime Server ──
flask_app = Flask('')

@flask_app.route('/')
def home(): return "✅ Bot is alive."

def run(): flask_app.run(host="0.0.0.0", port=8080)
def keep_alive(): Thread(target=run).start()

# ── Start ──
if __name__ == "__main__":
    keep_alive()
    print("✅ Bot running...")
    app.run()
