# 🤖 Contact Bot - Bot Development Services

A professional contact bot for handling client inquiries about custom Telegram bot development services.

## ✨ Features

### 🎯 Client Features
- **Interactive Menu System** - Easy navigation with inline buttons
- **Inquiry System** - Users can send detailed requirements
- **Service Information** - Pricing, portfolio, and service details
- **Anti-spam Protection** - Cooldown system to prevent spam
- **Professional Interface** - Clean and modern design

### 👨‍💻 Developer Features  
- **Inquiry Forwarding** - All user messages forwarded to you
- **Reply System** - Reply to users with `/reply <user_id> <message>`
- **Statistics Dashboard** - Track bot usage with `/stats`
- **User Management** - Monitor active users and inquiries

## 🚀 Quick Setup Guide

### 1. Create New Bot
```
1. Message @BotFather on Telegram
2. Send /newbot
3. Choose name: "YourName Contact Bot"  
4. Choose username: "YourNameContactBot"
5. Save the BOT_TOKEN
```

### 2. Get API Credentials
```
1. Go to https://my.telegram.org
2. Login with your phone number
3. Go to API Development Tools
4. Create new application
5. Save API_ID and API_HASH
```

### 3. Environment Variables
```bash
API_ID=your_api_id
API_HASH=your_api_hash  
BOT_TOKEN=your_bot_token_from_botfather
OWNER_ID=your_telegram_user_id
SUPPORT_GROUP=@YourSupportGroup
```

### 4. Deploy to Render
```
1. Create GitHub repository
2. Upload files (main.py, requirements.txt, README.md)
3. Connect to Render.com
4. Choose "Web Service"
5. Set environment variables
6. Deploy!
```

### 5. Setup 24/7 with UptimeRobot
```
1. Get your Render URL: https://yourapp.onrender.com
2. Create UptimeRobot account
3. Add HTTP monitor with your URL
4. Set interval to 5 minutes
5. Bot stays alive 24/7!
```

## 💬 Bot Commands

### For Users:
- `/start` - Welcome message and main menu
- `/help` - How to use the bot

### For Owner Only:
- `/reply <user_id> <message>` - Reply to user inquiry
- `/stats` - View bot statistics  
- `/broadcast <message>` - Send message to all users (Pro feature)

## 🎯 Usage Flow

1. **User starts bot** → Gets welcome message with options
2. **User clicks "Send Inquiry"** → Bot asks for requirements  
3. **User types message** → Forwarded to you instantly
4. **You reply with** `/reply <user_id> Your response`
5. **User gets reply** → Can continue conversation

## 📱 Integration with Main Bot

Add this to your Spy Bot's `/start` command:

```python
text = (
    # ... existing welcome text ...
    "\n🤖 *Want your own bot like this?*\n"
    "Contact: @YourNameContactBot"
)
```

## 🛠️ File Structure
```
contact-bot/
├── main.py              # Main bot code
├── requirements.txt     # Dependencies  
├── README.md           # This file
└── .env               # Environment variables (local only)
```

## 💰 Monetization Features

### Service Showcase:
- **Pricing Guide** - Different tiers and packages
- **Portfolio Display** - Previous work examples  
- **Service Categories** - Game bots, business bots, etc.
- **Professional Presentation** - Clean, modern interface

### Lead Management:
- **Inquiry Tracking** - All messages forwarded to you
- **User Information** - ID, username, timestamp included
- **Reply System** - Easy communication with prospects
- **Statistics** - Track bot usage and inquiries

## 🔧 Customization

### Change Services:
Edit the pricing and services in the `/start` and callback handlers.

### Modify Design:
Update button texts and messages in the code.

### Add Features:
- Database for user storage
- Payment integration
- File sharing capabilities
- Automated responses

## 📊 Success Metrics

- **Professional Appearance** ✅
- **Easy User Flow** ✅  
- **Instant Notifications** ✅
- **Anti-spam Protection** ✅
- **Mobile Optimized** ✅
- **24/7 Availability** ✅

## 🎯 Marketing Integration

Use this bot as:
- **Main contact point** for all bot development inquiries
- **Lead generator** from your existing bots
- **Professional showcase** of your services
- **Client communication hub**

## 📞 Support

For issues with this contact bot:
- Check environment variables
- Verify bot token and permissions
- Test with `/start` command
- Monitor Render logs for errors

---

**Ready to start getting bot development clients! 🚀**