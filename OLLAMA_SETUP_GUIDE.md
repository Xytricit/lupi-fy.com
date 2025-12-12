# 🚀 AI CHATBOT - QUICK SETUP (5 MINUTES)

## ⚡ Current Status

✅ **Django Server**: Running at http://127.0.0.1:8000
✅ **Chatbot Frontend**: Ready at http://127.0.0.1:8000/chatbot/
✅ **Database**: Connected
❌ **Ollama AI Engine**: NOT YET INSTALLED (required)

---

## 🎯 What You Need (2 Steps)

### Step 1: Install Ollama (The AI Engine)

**Download:** https://ollama.ai

1. Go to https://ollama.ai
2. Click "Download" for Windows
3. Run the installer and follow prompts
4. Restart your computer (optional but recommended)

### Step 2: Start Ollama

Open **PowerShell** and run:

```powershell
# Terminal 1: Start Ollama service
ollama serve

# Terminal 2: Download & run the AI model (one-time, ~4GB)
ollama run mistral
```

**Wait for it to finish downloading** (~5 minutes)

---

## ✅ Verify Everything Works

### Terminal 3: Check Ollama is running
```powershell
Invoke-WebRequest 'http://127.0.0.1:11434/api/tags' -UseBasicParsing
# Should return JSON with "mistral" model
```

### Check Django is running
```powershell
Invoke-WebRequest 'http://127.0.0.1:8000/chatbot/' -UseBasicParsing
# Should return status 200
```

---

## 🎮 Test the Chatbot

1. **Open browser**: http://127.0.0.1:8000/
2. **Log in** with your account credentials
3. **Visit**: http://127.0.0.1:8000/chatbot/
4. **Send a message**: "Hello! What should I post about?"
5. **Wait** 2-5 seconds for AI to respond
6. **Enjoy** your AI content coach!

---

## 🧠 Try These Prompts

```
"What should I post about?"
"How can I grow my engagement?"
"Give me content ideas"
"How am I doing so far?"
"I want to create a blog post"
"What's my creator level?"
```

---

## 🐛 If It Doesn't Work

### "Connection error" or "Service offline"
→ Make sure Ollama is running (`ollama serve`)

### "Login required"
→ Sign up/login at http://127.0.0.1:8000/ first

### AI responds very slowly (>10 seconds)
→ Mistral needs more RAM. Try:
```powershell
ollama run tinyllama  # Faster, smaller model
```

### Can't install Ollama
→ Make sure you have:
- Windows 10/11
- 4GB+ RAM (8GB recommended)
- Internet connection
- Administrator access

---

## 📊 System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 4 GB | 8+ GB |
| Disk Space | 5 GB | 10 GB |
| Ollama Model | Tinyllama | Mistral |
| Response Time | 5-10 sec | 2-5 sec |

---

## 📁 File Locations

```
Your Project:
├─ http://127.0.0.1:8000/          [Main site]
├─ http://127.0.0.1:8000/chatbot/  [AI Coach]
├─ http://127.0.0.1:8000/login/    [Login]
└─ http://127.0.0.1:8000/dashboard/[Dashboard]

Ollama (after install):
├─ Windows: C:\Program Files\Ollama\
├─ Command: ollama serve
└─ API: http://127.0.0.1:11434/
```

---

## ⚙️ Terminal Commands Reference

```powershell
# Start Ollama (Terminal 1)
ollama serve

# Download AI model (Terminal 2, first time only)
ollama run mistral

# Alternative faster model (if Mistral is slow)
ollama run tinyllama

# List installed models
ollama list

# Stop Ollama
# Press Ctrl+C in the terminal

# Django already running?
# Server is at: http://127.0.0.1:8000
```

---

## 🎯 Success Checklist

- [ ] Ollama installed (https://ollama.ai)
- [ ] `ollama serve` running in terminal
- [ ] `ollama run mistral` completed
- [ ] Django running at http://127.0.0.1:8000
- [ ] Logged into your account
- [ ] Can access http://127.0.0.1:8000/chatbot/
- [ ] Can send message and get response
- [ ] AI responds within 5 seconds
- [ ] Task buttons appear and work
- [ ] Analytics sidebar shows your stats

Once all ✅, you're ready to use your AI coach!

---

## 💡 Tips

1. **First run is slow**: Ollama needs to load the model (~5 seconds initially)
2. **Keep Ollama running**: Don't close the `ollama serve` terminal
3. **Multiple models**: You can install different models (see Ollama website)
4. **No internet needed**: Everything runs locally after download
5. **Privacy**: Your chats never leave your computer

---

## 🆘 Need Help?

**Still not working?**

Check Django logs:
```powershell
# Look for errors in the Django terminal
# Check: http://127.0.0.1:8000/admin/ for system status
```

**Ollama specific:**
- Website: https://ollama.ai
- Models: https://ollama.ai/library
- Help: https://ollama.ai/help

---

## 🎉 Once Everything Works

Your AI chatbot can:
- ✅ Analyze your content performance
- ✅ Give personalized growth advice
- ✅ Suggest content ideas
- ✅ Track your creator level
- ✅ Execute actions (create posts, navigate)
- ✅ Remember conversation history
- ✅ Run 100% locally (no costs, no privacy issues)

**Enjoy your AI content coach!** 🚀

---

**Time to setup**: ~15 minutes (mostly waiting for download)
**After setup**: Instant AI responses
**Cost**: FREE

Questions? Check the comprehensive guides:
- CHATBOT_QUICK_START.md
- CHATBOT_SUPERCHARGED.md
- CHATBOT_INTEGRATION.md
