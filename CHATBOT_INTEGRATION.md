# Quick Integration Guide - Adding Chatbot to Dashboard

## Option 1: Floating Chat Button (Recommended)

Add this to `dashboardhome.html` before the closing `</body>` tag:

```html
<!-- Floating Chatbot Widget -->
<a href="{% url 'chatbot_page' %}" class="floating-chat-btn" title="Open AI Chat">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    <span class="pulse"></span>
</a>

<style>
.floating-chat-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #1f9cee 0%, #167ac6 100%);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(31, 156, 238, 0.4);
    z-index: 999;
    text-decoration: none;
    transition: all 0.3s;
}

.floating-chat-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(31, 156, 238, 0.6);
}

.floating-chat-btn .pulse {
    position: absolute;
    width: 12px;
    height: 12px;
    background: #fec76f;
    border-radius: 50%;
    bottom: 4px;
    right: 4px;
    animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.5;
        transform: scale(1.2);
    }
}

@media (max-width: 768px) {
    .floating-chat-btn {
        bottom: 16px;
        right: 16px;
        width: 48px;
        height: 48px;
    }
}
</style>
```

---

## Option 2: Dashboard Widget (Sidebar)

Add to the dashboard sidebar section:

```html
<div class="dashboard-widget chat-widget">
    <h3>💬 Quick Chat</h3>
    <p>Need content ideas or growth advice?</p>
    <a href="{% url 'chatbot_page' %}" class="btn btn-primary">Open AI Coach</a>
</div>

<style>
.chat-widget {
    background: linear-gradient(135deg, #1f9cee 0%, #167ac6 100%);
    color: white;
    padding: 16px;
    border-radius: 8px;
    margin-bottom: 16px;
}

.chat-widget h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
}

.chat-widget p {
    margin: 0 0 12px 0;
    font-size: 14px;
    opacity: 0.9;
}

.chat-widget .btn {
    width: 100%;
    text-align: center;
}
</style>
```

---

## Option 3: Header Navigation Link

Add to the header navigation:

```html
<a href="{% url 'chatbot_page' %}" class="nav-item" title="AI Chat Assistant">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    <span class="label">AI Coach</span>
</a>
```

---

## Testing the Integration

1. **Start Django**: `python manage.py runserver`
2. **Start Ollama**: `ollama serve`
3. **Log in** to your account
4. **Click the chat button** to open chatbot
5. **Send a message** like "Hello!"
6. **Verify** the AI responds

---

## Custom Styling

To match your site theme, edit `chatbot.css`:

```css
/* Change primary color */
:root {
  --primary: #1f9cee;      /* Change this */
  --primary-dark: #167ac6; /* And this */
  --accent: #fec76f;       /* And this */
}
```

---

## Disable Chatbot (If Needed)

Remove the URL from `mysite/urls.py`:
```python
# Comment out:
# path("chatbot/", include("chatbot.urls")),
```

---

## Monitor Performance

The chatbot uses Django cache, which by default uses memory. To monitor:

1. Check cache hit rate in Django logs
2. Monitor Ollama response times (should be < 5 seconds)
3. Review conversation history in Django cache

---

## Need Help?

Refer to `CHATBOT_SUPERCHARGED.md` for:
- Full feature documentation
- Troubleshooting guide
- API endpoints
- Customization options
