from telethon import TelegramClient, events
import os
import threading
import asyncio
import multiprocessing, asyncio
import aiohttp
from flask import Flask
from db import init_db, add_user, get_all_users
import re

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
                await session.get("https://nkcontactbot.onrender.com")  # Yaha apna URL daalna
                print("🌐 Keep-alive ping sent!")
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

def detect_keywords(text):
    """Detect keywords in user message"""
    text = text.lower()
    
    # Bot request keywords
    bot_keywords = ['bot', 'clone', 'similar', 'jaisa', 'same', 'chahiye', 'banao', 'bana do']
    
    # My bots keywords
    mybots_keywords = ['bots', 'projects', 'work', 'banaya', 'dekho', 'show', 'projects']
    
    # Contact/help keywords
    contact_keywords = ['contact', 'help', 'inquiry', 'query', 'question', 'puchna', 'baat']
    
    # Support keywords  
    support_keywords = ['support', 'group', 'join', 'community', 'channel']
    
    if any(word in text for word in bot_keywords):
        return 'bot_request'
    elif any(word in text for word in mybots_keywords):
        return 'my_bots'
    elif any(word in text for word in support_keywords):
        return 'support'
    elif any(word in text for word in contact_keywords):
        return 'contact'
    else:
        return 'general'

@client.on(events.NewMessage(pattern='^/start$'))
async def start_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    welcome_text = (
        "👋 <b>Hey! Welcome to my Contact Bot!</b>\n\n"
        "🤖 <b>What I can help you with:</b>\n"
        "• Want a bot like mine? I can guide you!\n"
        "• Need help with Telegram bots? Ask away!\n"
        "• Got questions? I'm here to answer!\n"
        "• Want to see what I've built? Check it out!\n\n"
        "💡 <b>My Current Bots:</b>\n"
        "• Spy x Civilians Game Bot 🎮\n"
        "• This Contact Bot 📞\n"
        "• More coming soon...\n\n"
        "🎯 <b>Quick Commands:</b>\n"
        "• Type <code>/mybots</code> to see my projects\n"
        "• Type <code>/request</code> to ask for help\n"
        "• Type <code>/support</code> for community group\n"
        "• Just ask me anything in simple words!\n\n"
        "💬 <b>I'm here to help, not sell anything!</b> 😊"
    )
    
    await event.respond(welcome_text, parse_mode="html")

    # Save user id (persistent in Postgre)
    uid = event.sender_id
    await asyncio.to_thread(add_user, uid)

@client.on(events.NewMessage(pattern='^/help$'))
async def help_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    help_text = (
        "📖 <b>How to use this bot:</b>\n\n"
        "🎯 <b>Available Commands:</b>\n"
        "• <code>/mybots</code> - See what I've built\n"
        "• <code>/request</code> - Ask for help or bot clone\n" 
        "• <code>/support</code> - Join our community\n\n"
        "💬 <b>Or just chat normally:</b>\n"
        "• 'I want a bot like spy game'\n"
        "• 'Can you help me with...?'\n"
        "• 'Show me your bots'\n"
        "• 'I need similar bot'\n\n"
        "🤝 <b>What I do:</b>\n"
        "• Help fellow developers\n"
        "• Share bot clones if possible\n"
        "• Answer your questions\n"
        "• Build community together\n\n"
        f"📞 <b>Quick support:</b> Join {SUPPORT_GROUP}"
    )
    
    await event.respond(help_text, parse_mode="html")

@client.on(events.NewMessage(pattern='^/(mybots|bots|projects)$'))
async def mybots_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    mybots_text = (
        "🤖 <b>My Current Bot Projects:</b>\n\n"
        "🎮 <b>Spy x Civilians Game Bot</b>\n"
        "• Multiplayer group game\n"
        "• Multiple game modes\n"
        "• Anti-spam & admin controls\n"
        "• Database integration\n"
        "• Currently active & running!\n\n"
        "📞 <b>This Contact Bot</b>\n"
        "• Helps people connect with me\n"
        "• Query handling system\n"
        "• Community building tool\n\n"
        "🚀 <b>Future Projects:</b>\n"
        "• More game bots\n"
        "• Utility bots\n"
        "• Community tools\n\n"
        "Want something similar? Just ask!\n"
        "I'll help if I can! 😊\n\n"
        f"📢 Updates & showcases: {SUPPORT_GROUP}"
    )
    
    await event.respond(mybots_text, parse_mode="html")

@client.on(events.NewMessage(pattern='^/(request|help_me)$'))
async def request_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    user_states[event.sender_id] = "waiting_request"
    
    request_text = (
        "🤝 <b>Sure! I'd love to help:</b>\n\n"
        "Please tell me what you need:\n\n"
        "🎯 <b>Examples:</b>\n"
        "• 'I want a bot like your spy game'\n"
        "• 'Can you make a similar contact bot?'\n"
        "• 'Help me understand how bots work'\n"
        "• 'I have a question about...'\n\n"
        "💭 <b>Be specific about:</b>\n"
        "• What kind of bot you want\n"
        "• Which features you need\n"
        "• Any specific requirements\n\n"
        "📝 <b>Just describe your needs and I'll see how I can help!</b>\n\n"
        "Note: I help based on availability & interest 😊"
    )
    
    await event.respond(request_text, parse_mode="html")

@client.on(events.NewMessage(pattern='^/(support|group|community)$'))
async def support_cmd(event):
    if await is_spam(event.sender_id):
        return
        
    group_text = (
        "👥 <b>Join Our Bot Community!</b>\n\n"
        f"🔗 <b>Support Group:</b> {SUPPORT_GROUP}\n\n"
        "<b>What's in the group:</b>\n"
        "• Bot showcases & demos\n"
        "• New project announcements\n"
        "• Community discussions\n"
        "• Bot development tips\n"
        "• Direct interaction with me\n"
        "• See my bots in action!\n\n"
        "🎮 <b>Try my Spy Game bot there!</b>\n"
        "💬 <b>Get quick help & support</b>\n"
        "📢 <b>Stay updated with new bots</b>\n\n"
        f"<b>Join here:</b> https://t.me/{SUPPORT_GROUP.replace('@', '')}\n\n"
        "🤝 <b>Let's build an awesome bot community together!</b>"
    )
    
    await event.respond(group_text, parse_mode="html")

# Handle all text messages with keyword detection
@client.on(events.NewMessage)
async def handle_messages(event):
    if event.raw_text.startswith('/'):
        return  # Skip commands that are already handled
    
    if await is_spam(event.sender_id):
        await event.respond("⚠️ Please wait a few seconds between messages.")
        return
    
    user_id = event.sender_id
    message_text = event.raw_text.strip()
    
    # Check if user is in request mode
    if user_states.get(user_id) == "waiting_request":
        user = await client.get_entity(user_id)
        
        # Forward request to owner
        request_message = (
            f"📨 <b>New Help Request!</b>\n\n"
            f"👤 <b>From:</b> {mention_user(user)}\n"
            f"🆔 <b>User ID:</b> <code>{user_id}</code>\n"
            f"👤 <b>Username:</b> @{user.username if user.username else 'No username'}\n"
            f"📅 <b>Date:</b> {event.date.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💬 <b>Request:</b>\n{message_text}\n\n"
            f"📞 <b>Reply with:</b> <code>/reply {user_id} Your message here</code>"
        )
        
        try:
            await client.send_message(OWNER_ID, request_message, parse_mode="html")
            
            # Confirm to user
            await event.respond(
                "✅ <b>Request received!</b>\n\n"
                "📬 I've got your message and will get back to you soon!\n"
                "⏰ I'll respond when I'm available.\n\n"
                f"💬 Meanwhile, feel free to join {SUPPORT_GROUP} for community support!\n\n"
                "🤝 <b>Thanks for reaching out!</b>",
                parse_mode="html"
            )
            
            # Reset user state
            user_states[user_id] = None
            
        except Exception as e:
            await event.respond(
                "❌ <b>Oops! Something went wrong.</b>\n\n"
                f"Please try joining {SUPPORT_GROUP} directly for support!"
            )
        
        return  # Don't process keywords if in request mode
    
    # Detect keywords and respond accordingly
    keyword_type = detect_keywords(message_text)
    
    if keyword_type == 'bot_request':
        await event.respond(
            "🤖 <b>You want a bot? Cool!</b>\n\n"
            "I can help if I have time and interest!\n\n"
            "🎯 <b>What I currently have:</b>\n"
            "• Spy x Civilians Game Bot\n"
            "• This Contact Bot\n\n"
            "Want something similar? Type <code>/request</code> and describe what you need!\n\n"
            "🤝 <b>I'll see how I can help!</b>",
            parse_mode="html"
        )
        
    elif keyword_type == 'my_bots':
        await event.respond(
            "🎮 <b>Here's what I've built so far:</b>\n\n"
            "• Spy x Civilians Game Bot (Active)\n"
            "• This Contact Bot (You're using it!)\n\n"
            "More projects coming soon!\n\n"
            "Type <code>/mybots</code> for detailed info\n"
            f"Or join {SUPPORT_GROUP} to see them in action!",
            parse_mode="html"
        )
        
    elif keyword_type == 'support':
        await event.respond(
            "👥 <b>Join our community!</b>\n\n"
            f"🔗 {SUPPORT_GROUP}\n\n"
            "• See my bots in action\n"
            "• Get help from community\n"
            "• Stay updated with new projects\n\n"
            "Type <code>/support</code> for more details!",
            parse_mode="html"
        )
        
    elif keyword_type == 'contact':
        user_states[user_id] = "waiting_request"
        await event.respond(
            "💬 <b>Sure! What can I help you with?</b>\n\n"
            "Please describe:\n"
            "• What you need help with\n"
            "• Any specific questions\n"
            "• Bot requests or queries\n\n"
            "📝 Just type your message and I'll get back to you!\n\n"
            "🤝 <b>Always happy to help fellow developers!</b>",
            parse_mode="html"
        )
        
    else:
        # General response with suggestions
        await event.respond(
            "👋 <b>Hey there!</b>\n\n"
            "I'm here to help with bot-related stuff!\n\n"
            "🎯 <b>You can:</b>\n"
            "• Ask for help: 'I need help with...'\n"
            "• Request bots: 'I want a bot like...'\n"
            "• See my work: 'Show me your bots'\n"
            "• Join community: 'Support group'\n\n"
            "💬 <b>Or just ask me anything!</b>\n\n"
            "🤝 I'm here to help, not to sell anything! 😊",
            parse_mode="html"
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
            f"🤝 <b>Response from me:</b>\n\n"
            f"{message}\n\n"
            f"💬 <b>Continue chatting:</b> {SUPPORT_GROUP}\n"
            f"📞 <b>More questions?</b> Just ask here!"
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
    
    total_users = await asyncio.to_thread(get_all_users)
    
    stats_text = (
        f"📊 <b>Bot Statistics:</b>\n\n"
        f"👥 <b>Total Users:</b> {len(total_users)}\n"
        f"💬 <b>Active Users:</b> {len(last_message_time)}\n"
        f"📝 <b>Users in Request Mode:</b> {len([u for u, s in user_states.items() if s == 'waiting_request'])}\n"
        f"⚡ <b>Bot Status:</b> Running\n\n"
        f"📞 <b>Commands:</b>\n"
        f"<code>/reply <user_id> <message></code> - Reply to user\n"
        f"<code>/broadcast <message></code> - Send broadcast\n"
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