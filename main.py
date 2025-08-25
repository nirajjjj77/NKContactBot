from telethon import TelegramClient, events, Button
import os
import threading
import asyncio
from flask import Flask

# Flask app for Render (dummy endpoint)
app = Flask(__name__)

@app.route('/')
def home():
    return "Contact Bot is running! 🤖"

@app.route('/health')
def health():
    return "OK"

def run_web():
    app.run(host="0.0.0.0", port=10000)

# Start flask server in background
threading.Thread(target=run_web, daemon=True).start()

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
        "👋 **Welcome to Bot Development Services!**\n\n"
        "🤖 **I help you create custom Telegram bots like:**\n"
        "• Game Bots (Spy x Civilians, Quiz, etc.)\n"
        "• Business Bots (Shop, Support, etc.)\n"
        "• Utility Bots (File converter, Weather, etc.)\n"
        "• Custom Features & Modifications\n\n"
        "💡 **Services Available:**\n"
        "• Custom Bot Development\n"
        "• Bot Modifications & Updates\n"
        "• 24/7 Hosting Setup (Render + UptimeRobot)\n"
        "• Database Integration (PostgreSQL)\n"
        "• Bot Maintenance & Support\n\n"
        "💰 **Pricing:** Affordable & Negotiable\n"
        "⚡ **Delivery:** Fast & Quality work\n\n"
        "Choose an option below to get started:"
    )
    
    buttons = [
        [Button.inline("💬 Send Inquiry", b"send_inquiry")],
        [Button.inline("💰 View Pricing", b"view_pricing")],
        [Button.inline("🔗 Join Support Group", b"join_group")],
        [Button.inline("📱 View Portfolio", b"view_portfolio")]
    ]
    
    await event.respond(welcome_text, buttons=buttons, parse_mode="markdown")

@client.on(events.NewMessage(pattern='^/help$'))
async def help_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    help_text = (
        "📖 **How to use this bot:**\n\n"
        "1️⃣ Send `/start` to see main menu\n"
        "2️⃣ Click 'Send Inquiry' to describe your requirements\n"
        "3️⃣ I'll get back to you within 24 hours\n"
        "4️⃣ We discuss details and pricing\n"
        "5️⃣ Development starts after agreement\n\n"
        "🔄 **Process:**\n"
        "• Requirement Analysis\n"
        "• Development & Testing\n"
        "• Deployment & Setup\n"
        "• Support & Maintenance\n\n"
        "📞 **Need immediate help?** Join: " + SUPPORT_GROUP
    )
    
    await event.respond(help_text, parse_mode="markdown")

@client.on(events.CallbackQuery)
async def callback_handler(event):
    if await is_spam(event.sender_id):
        return
        
    data = event.data.decode()
    
    if data == "send_inquiry":
        user_states[event.sender_id] = "waiting_inquiry"
        inquiry_text = (
            "✍️ **Please describe your bot requirements:**\n\n"
            "Include details like:\n"
            "• What type of bot you want\n"
            "• Key features needed\n"
            "• Your budget range\n"
            "• Timeline expectations\n"
            "• Any specific requirements\n\n"
            "📝 **Just type your message and I'll forward it to the developer!**"
        )
        await event.edit(inquiry_text, parse_mode="markdown")
    
    elif data == "view_pricing":
        pricing_text = (
            "💰 **Service Pricing Guide:**\n\n"
            "🤖 **Simple Bots:** $10-30\n"
            "• Basic commands\n"
            "• Simple responses\n"
            "• No database needed\n\n"
            "🎮 **Game Bots:** $30-80\n"
            "• Interactive games\n"
            "• Multi-user support\n"
            "• Score tracking\n\n"
            "🏪 **Business Bots:** $50-150\n"
            "• E-commerce features\n"
            "• Payment integration\n"
            "• Admin panels\n\n"
            "🔧 **Custom Features:** $20-100\n"
            "• Database integration\n"
            "• API connections\n"
            "• Advanced functionality\n\n"
            "📦 **Complete Package:** Bot + Hosting + Support\n\n"
            "💡 **Final price depends on complexity!**"
        )
        
        buttons = [
            [Button.inline("💬 Discuss My Project", b"send_inquiry")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(pricing_text, buttons=buttons, parse_mode="markdown")
    
    elif data == "join_group":
        group_text = (
            "👥 **Join our Support Community:**\n\n"
            f"🔗 **Support Group:** {SUPPORT_GROUP}\n\n"
            "**What you get:**\n"
            "• Free bot development tips\n"
            "• Community support\n"
            "• Updates on new services\n"
            "• Direct communication\n"
            "• Showcase of completed projects\n\n"
            "**Join now for instant support!**"
        )
        
        buttons = [
            [Button.url("📱 Join Support Group", f"https://t.me/{SUPPORT_GROUP.replace('@', '')}")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(group_text, buttons=buttons, parse_mode="markdown")
    
    elif data == "view_portfolio":
        portfolio_text = (
            "🏆 **Previous Work & Portfolio:**\n\n"
            "🎮 **Spy x Civilians Bot**\n"
            "• Multiplayer game bot\n"
            "• 4 different game modes\n"
            "• Database integration\n"
            "• Anti-spam system\n"
            "• Admin controls\n\n"
            "🔧 **Technical Skills:**\n"
            "• Python (Telethon, Pyrogram)\n"
            "• Database (PostgreSQL, MongoDB)\n"
            "• Hosting (Render, Heroku, VPS)\n"
            "• 24/7 Uptime Setup\n"
            "• Payment Integration\n"
            "• Web Scraping & APIs\n\n"
            "✅ **100% Client Satisfaction**\n"
            "✅ **Post-delivery Support**\n"
            "✅ **Source Code Provided**"
        )
        
        buttons = [
            [Button.inline("💬 Start My Project", b"send_inquiry")],
            [Button.inline("🔙 Back to Main", b"back_main")]
        ]
        
        await event.edit(portfolio_text, buttons=buttons, parse_mode="markdown")
    
    elif data == "back_main":
        # Resend the start message
        await start_cmd(event)

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
            f"📨 **New Bot Inquiry!**\n\n"
            f"👤 **From:** {mention_user(user)}\n"
            f"🆔 **User ID:** `{user_id}`\n"
            f"👤 **Username:** @{user.username if user.username else 'No username'}\n"
            f"📅 **Date:** {event.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💬 **Message:**\n{event.raw_text}\n\n"
            f"📞 **Reply with:** `/reply {user_id} Your message here`"
        )
        
        try:
            await client.send_message(OWNER_ID, inquiry_message, parse_mode="markdown")
            
            # Confirm to user
            await event.respond(
                "✅ **Inquiry sent successfully!**\n\n"
                "📬 Your message has been forwarded to the developer.\n"
                "⏰ You'll get a response within 24 hours.\n\n"
                f"💬 Or join {SUPPORT_GROUP} for immediate assistance!",
                parse_mode="markdown"
            )
            
            # Reset user state
            user_states[user_id] = None
            
        except Exception as e:
            await event.respond(
                "❌ **Sorry, there was an error sending your message.**\n\n"
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
            f"👨‍💻 **Developer Reply:**\n\n"
            f"{message}\n\n"
            f"💬 **Continue discussion:** {SUPPORT_GROUP}\n"
            f"📞 **Need clarification?** Just reply here!"
        )
        
        await client.send_message(user_id, reply_message, parse_mode="markdown")
        await event.respond(f"✅ Reply sent to user {user_id}")
        
    except Exception as e:
        await event.respond(f"❌ Error sending reply: {str(e)}")

# Owner broadcast system
@client.on(events.NewMessage(pattern=r'^/broadcast (.+)'))
async def broadcast_message(event):
    if event.sender_id != OWNER_ID:
        return
    
    # This is a simple version - you can add database to store all users
    await event.respond("🔄 Broadcast feature available in full version with database!")

@client.on(events.NewMessage(pattern='^/stats$'))
async def stats_cmd(event):
    if event.sender_id != OWNER_ID:
        return
    
    stats_text = (
        f"📊 **Bot Statistics:**\n\n"
        f"👥 **Active Users:** {len(last_message_time)}\n"
        f"💬 **Users in Inquiry Mode:** {len([u for u, s in user_states.items() if s == 'waiting_inquiry'])}\n"
        f"⚡ **Bot Status:** Running\n\n"
        f"📞 **Commands:**\n"
        f"`/reply <user_id> <message>` - Reply to user\n"
        f"`/broadcast <message>` - Broadcast (Pro version)\n"
        f"`/stats` - Show statistics"
    )
    
    await event.respond(stats_text, parse_mode="markdown")

print("🤖 Contact Bot is running...")
client.run_until_disconnected()