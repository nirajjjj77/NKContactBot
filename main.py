from telethon import TelegramClient, events, Button
import os
import threading
import asyncio
import multiprocessing, asyncio
import aiohttp
from flask import Flask
from db import init_db, add_user, get_all_users

# Initialize database tables
init_db()

# Flask app for Render (dummy endpoint)
app = Flask(__name__)

@app.route('/')
def home():
    return "Contact Bot is running! 🤖"

def run_web():
    # Run flask on separate process (not thread, avoids asyncio loop conflicts)
    app.run(host="0.0.0.0", port=10000)

async def keep_alive():
    """Periodically ping the Render URL to prevent sleeping"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                await session.get("https://nkcontactbot.onrender.com")  # Yaha apna URL daalना
                print("🌍 Keep-alive ping sent!")
        except Exception as e:
            print(f"⚠️ Keep-alive failed: {e}")
        await asyncio.sleep(300)  # every 5 minutes

# Bot configuration
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 0))  # Your Telegram user ID
SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "@YourSupportGroup")  # Your support group username

client = TelegramClient('contact_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Anti-spam system
user_states = {}  # user_id -> state
last_message_time = {}  # user_id -> timestamp
COOLDOWN_TIME = 3  # seconds between messages

def get_current_time():
    return asyncio.get_event_loop().time()

async def is_spam(user_id):
    current_time = get_current_time()
    last_time = last_message_time.get(user_id, 0)
    
    if current_time - last_time < COOLDOWN_TIME:
        return True
    
    last_message_time[user_id] = current_time
    return False

def mention_user(user):
    return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

@client.on(events.NewMessage(pattern='^/start$'))
async def start_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    welcome_text = (
        "👋 <b>Welcome to Bot Development Services!</b>\n\n"
        "🤖 <b>I help you create custom Telegram bots like:</b>\n"
        "• Game Bots (Spy x Civilians, Quiz, etc.)\n"
        "• Business Bots (Shop, Support, etc.)\n"
        "• Utility Bots (File converter, Weather, etc.)\n"
        "• Custom Features & Modifications\n\n"
        "💡 <b>Services Available:</b>\n"
        "• Custom Bot Development\n"
        "• Bot Modifications & Updates\n"
        "• 24/7 Hosting Setup (Render + UptimeRobot)\n"
        "• Database Integration (PostgreSQL)\n"
        "• Bot Maintenance & Support\n\n"
        "💰 <b>Pricing:</b> Affordable & Negotiable\n"
        "⚡ <b>Delivery:</b> Fast & Quality work\n\n"
        "Choose an option below to get started:"
    )
    
    buttons = [
        [Button.inline("💬 Send Inquiry", b"send_inquiry")],
        [Button.inline("💰 View Pricing", b"view_pricing")],
        [Button.inline("🔗 Join Support Group", b"join_group")],
        [Button.inline("📱 View Portfolio", b"view_portfolio")]
    ]
    
    await event.respond(welcome_text, buttons=buttons, parse_mode="html")

    #Save user id (persistent in Postgre)
    uid = event.sender_id
    await asyncio.to_thread(add_user, uid)

@client.on(events.NewMessage(pattern='^/help$'))
async def help_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    help_text = (
        "📖 <b>How to use this bot:*</b>\n\n"
        "1️⃣ Send <code>/start</code> to see main menu\n"
        "2️⃣ Click 'Send Inquiry' to describe your requirements\n"
        "3️⃣ I'll get back to you within 24 hours\n"
        "4️⃣ We discuss details and pricing\n"
        "5️⃣ Development starts after agreement\n\n"
        "🔄 <b>Process:</b>\n"
        "• Requirement Analysis\n"
        "• Development & Testing\n"
        "• Deployment & Setup\n"
        "• Support & Maintenance\n\n"
        "📞 <b>Need immediate help?</b> Join: " + SUPPORT_GROUP
    )
    
    await event.respond(help_text, parse_mode="html")

@client.on(events.CallbackQuery)
async def callback_handler(event):
    if await is_spam(event.sender_id):
        return
        
    data = event.data.decode()
    
    if data == "send_inquiry":
        user_states[event.sender_id] = "waiting_inquiry"
        inquiry_text = (
            "✍️ <b>Please describe your bot requirements:</b>\n\n"
            "Include details like:\n"
            "• What type of bot you want\n"
            "• Key features needed\n"
            "• Your budget range\n"
            "• Timeline expectations\n"
            "• Any specific requirements\n\n"
            "📝 <b>Just type your message and I'll forward it to the developer!</b>"
        )
        await event.edit(inquiry_text, parse_mode="html")
    
    elif data == "view_pricing":
        pricing_text = (
            "💰 <b>Service Pricing Guide:</b>\n\n"
            "🤖 <b>Simple Bots:*</b>$10-30\n"
            "• Basic commands\n"
            "• Simple responses\n"
            "• No database needed\n\n"
            "🎮 <b>Game Bots:</b> $30-80\n"
            "• Interactive games\n"
            "• Multi-user support\n"
            "• Score tracking\n\n"
            "🏪 <b>Business Bots:</b> $50-150\n"
            "• E-commerce features\n"
            "• Payment integration\n"
            "• Admin panels\n\n"
            "🔧 <b>Custom Features:</b> $20-100\n"
            "• Database integration\n"
            "• API connections\n"
            "• Advanced functionality\n\n"
            "📦 <b>Complete Package:</b> Bot + Hosting + Support\n\n"
            "💡 <b>Final price depends on complexity!</b>"
        )
        
        buttons = [
            [Button.inline("💬 Discuss My Project", b"send_inquiry")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(pricing_text, buttons=buttons, parse_mode="html")
    
    elif data == "join_group":
        group_text = (
            "👥 <b>Join our Support Community:</b>\n\n"
            f"🔗 <b>Support Group:</b> {SUPPORT_GROUP}\n\n"
            "<b>What you get:</b>\n"
            "• Free bot development tips\n"
            "• Community support\n"
            "• Updates on new services\n"
            "• Direct communication\n"
            "• Showcase of completed projects\n\n"
            "<b>Join now for instant support!</b>"
        )
        
        buttons = [
            [Button.url("📱 Join Support Group", f"https://t.me/{SUPPORT_GROUP.replace('@', '')}")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(group_text, buttons=buttons, parse_mode="html")
    
    elif data == "view_portfolio":
        portfolio_text = (
            "🏆 <b>Previous Work & Portfolio:</b>\n\n"
            "🎮 <b>Spy x Civilians Bot</b>\n"
            "• Multiplayer game bot\n"
            "• 4 different game modes\n"
            "• Database integration\n"
            "• Anti-spam system\n"
            "• Admin controls\n\n"
            "🔧 <b>Technical Skills:</b>\n"
            "• Python (Telethon, Pyrogram)\n"
            "• Database (PostgreSQL, MongoDB)\n"
            "• Hosting (Render, Heroku, VPS)\n"
            "• 24/7 Uptime Setup\n"
            "• Payment Integration\n"
            "• Web Scraping & APIs\n\n"
            "✅ <b>100% Client Satisfaction</b>\n"
            "✅ <b>Post-delivery Support</b>\n"
            "✅ <b>Source Code Provided</b>"
        )
        
        buttons = [
            [Button.inline("💬 Start My Project", b"send_inquiry")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(portfolio_text, buttons=buttons, parse_mode="html")
    
    elif data == "back_main":
        await event.edit(
            "👋 <b>Welcome to Bot Development Services!</b>\n\n"
            "🤖 <b>I help you create custom Telegram bots like:</b>\n"
            "• Game Bots (Spy x Civilians, Quiz, etc.)\n"
            "• Business Bots (Shop, Support, etc.)\n"
            "• Utility Bots (File converter, Weather, etc.)\n"
            "• Custom Features & Modifications\n\n"
            "💡 <b>Services Available:</b>\n"
            "• Custom Bot Development\n"
            "• Bot Modifications & Updates\n"
            "• 24/7 Hosting Setup (Render + UptimeRobot)\n"
            "• Database Integration (PostgreSQL)\n"
            "• Bot Maintenance & Support\n\n"
            "💰 <b>Pricing:</b> Affordable & Negotiable\n"
            "⚡ <b>Delivery:</b> Fast & Quality work\n\n"
            "Choose an option below to get started:",
            buttons=[
                [Button.inline("💬 Send Inquiry", b"send_inquiry")],
                [Button.inline("💰 View Pricing", b"view_pricing")],
                [Button.inline("🔗 Join Support Group", b"join_group")],
                [Button.inline("📱 View Portfolio", b"view_portfolio")]
            ],
            parse_mode="html"
        )

# Handle user inquiries
@client.on(events.NewMessage)
async def handle_messages(event):
    if event.raw_text.startswith('/'):
        return  # Skip commands
    
    if await is_spam(event.sender_id):
        await event.respond("⚠️ Please wait a few seconds between messages.")
        return
    
    user_id = event.sender_id
    
    # Check if user is in inquiry mode
    if user_states.get(user_id) == "waiting_inquiry":
        user = await client.get_entity(user_id)
        
        # Forward inquiry to owner
        inquiry_message = (
            f"📨 <b>New Bot Inquiry!</b>\n\n"
            f"👤 <b>From:</b> {mention_user(user)}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Username:</b> @{user.username if user.username else 'No username'}\n"
            f"📅 <b>Date:</b> {event.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💬 <b>Message:</b>\n{event.raw_text}\n\n"
            f"📞 <b>Reply with:</b> <code>/reply {user_id} Your message here</code>"
        )
        
        try:
            await client.send_message(OWNER_ID, inquiry_message, parse_mode="html")
            
            # Confirm to user
            await event.respond(
                "✅ <b>Inquiry sent successfully!</b>\n\n"
                "📬 Your message has been forwarded to the developer.\n"
                "⏰ You'll get a response within 24 hours.\n\n"
                f"💬 Or join {SUPPORT_GROUP} for immediate assistance!",
                parse_mode="html"
            )
            
            # Reset user state
            user_states[user_id] = None
            
        except Exception as e:
            await event.respond(
                "❌ <b>Sorry, there was an error sending your message.</b>\n\n"
                f"Please try joining {SUPPORT_GROUP} directly for support."
            )

# Owner reply system
@client.on(events.NewMessage(pattern=r'^/reply (\d+) (.+)'))
async def reply_to_user(event):
    if event.sender_id != OWNER_ID:
        return
    
    try:
        user_id = int(event.pattern_match.group(1))
        message = event.pattern_match.group(2)
        
        reply_message = (
            f"👨‍💻 <b>Developer Reply:</b>\n\n"
            f"{message}\n\n"
            f"💬 <b>Continue discussion:</b> {SUPPORT_GROUP}\n"
            f"📞 <b>Need clarification?</b> Just reply here!"
        )
        
        await client.send_message(user_id, reply_message, parse_mode="html")
        await event.respond(f"✅ Reply sent to user {user_id}")
        
    except Exception as e:
        await event.respond(f"❌ Error sending reply: {str(e)}")

# Owner broadcast system
@client.on(events.NewMessage(pattern='^/broadcast'))
async def broadcast_message(event):
    if event.sender_id != OWNER_ID:
        return

    args = event.raw_text.split(" ", 1)
    if len(args) < 2 or not args[1].strip():
        await event.respond("⚠️ Usage: /broadcast <message>")
        return

    msg = args[1].strip()
    sent = 0
    failed = 0

    user_ids = await asyncio.to_thread(get_all_users)
    for uid in user_ids:
        try:
            await client.send_message(uid, msg, parse_mode="html")
            sent += 1
            await asyncio.sleep(0.1)  # small delay, avoid flood
        except:
            failed += 1

    await event.respond(f"✅ Broadcast complete!\n📨 Sent: {sent}\n❌ Failed: {failed}")


@client.on(events.NewMessage(pattern='^/stats$'))
async def stats_cmd(event):
    if event.sender_id != OWNER_ID:
        return
    
    stats_text = (
        f"📊 <b>Bot Statistics:</b>\n\n"
        f"👥 <b>Active Users:</b> {len(last_message_time)}\n"
        f"💬 <b>Users in Inquiry Mode:</b> {len([u for u, s in user_states.items() if s == 'waiting_inquiry'])}\n"
        f"⚡ <b>Bot Status:</b> Running\n\n"
        f"📞 <b>Commands:</b>\n"
        f"<code>/reply <user_id> <message></code> - Reply to user\n"
        f"<code>/broadcast <message></code> - Broadcast (Pro version)\n"
        f"<code>/stats</code> - Show statistics"
    )
    
    await event.respond(stats_text, parse_mode="html")

if __name__ == "__main__":
    # Run Flask in separate process
    multiprocessing.Process(target=run_web, daemon=True).start()
    # Start keep-alive inside Telethon loop
    client.loop.create_task(keep_alive())
    # Run bot (manages its own event loop)
    print("🤖 Contact Bot is running...")
    client.run_until_disconnected()