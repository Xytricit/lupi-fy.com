# 🎨 LUPIFY COMPLETE TEMPLATE & CSS REFERENCE
## All Template HTML Files & Stylesheets

---

## 📋 QUICK FILE LOCATION GUIDE

```
templates/
├── dashboardhome.html              ← Main Dashboard
├── index.html                      ← Home page
├── search_results.html             ← Search results
├── terms.html                      ← Terms of Service
├── base.html                       ← Base template
├── auth_base.html                  ← Auth template
├── core/
│   ├── about.html                  ← About page
│   ├── contact.html                ← Contact page
│   └── lupiforge_guide.html        ← Platform guide
├── marketplace/
│   ├── home.html                   ← Marketplace home
│   ├── creator_dashboard.html      ← Creator analytics
│   ├── project_detail.html         ← Project details
│   ├── upload.html                 ← Upload project
│   ├── library.html                ← User's library
│   └── index.html                  ← Base for marketplace
├── games/
│   ├── dashboard.html              ← Games dashboard
│   ├── editor.html                 ← Game editor
│   ├── editor_enhanced.html        ← Enhanced editor
│   ├── multiplayer.html            ← Multiplayer games
│   ├── tutorial.html               ← Game tutorial
│   ├── moderation.html             ← Game moderation
│   └── creator_dashboard.html      ← Creator dashboard
└── chatbot/
    └── (various chat templates)

static/
├── css/
│   ├── dashboard.css               ← Main dashboard styles
│   ├── dashboard-complete.css      ← Dashboard complete styles
│   ├── dashboard-fixes.css         ← Dashboard fixes
│   ├── dashboard-inline.css        ← Inline dashboard styles
│   ├── main.css                    ← Main styles
│   ├── chatbot.css                 ← Chatbot styles
│   └── (other specialized CSS)
├── js/
│   ├── dashboard.js                ← Dashboard JavaScript
│   ├── chatbot.js                  ← Chatbot JS
│   ├── game-execution-engine.js    ← Game engine
│   ├── websocket-fallback.js       ← WebSocket handler
│   └── (other JS files)
├── style.css                       ← Main stylesheet
└── script.js                       ← Main JavaScript
```

---

# ⭐ KEY TEMPLATE FILES

## File: templates/dashboardhome.html
### MAIN DASHBOARD - User Home Feed

This is the main dashboard after login. Key sections:
- Recently played games carousel
- Filter bubbles (For you, Latest, Most liked, etc.)
- Blog recommendations grid
- Community posts feed
- Notification system
- Create post modal

**Size:** 2,275 lines
**Key Features:**
- User game history
- Dynamic feed loading
- Search suggestions
- Community posts API integration
- Theme switching
- Notifications bell with dropdown
- Avatar menu with user actions

**Top of File (Lines 1-150):**
```html
{% load static %}

<!DOCTYPE html>

<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
{% if request.user.is_authenticated %}
<meta name="current-user-id" content="{{ request.user.id }}">
{% endif %}
<title>{% block title %}Lupify - Dashboard{% endblock %}</title>
<link rel="stylesheet" href="{% static 'css/main.css' %}">
<link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
<link rel="stylesheet" href="{% static 'css/dashboard-complete.css' %}">
<link rel="stylesheet" href="{% static 'css/dashboard-fixes.css' %}">
    {% block extra_css %}{% endblock %}
        <script>
        (function(){
            try{
                const serverTheme = "{{ request.user.theme_preference|default:'' }}";
                if(serverTheme === 'dark') document.documentElement.setAttribute('data-theme','dark');
                else if(serverTheme === 'light') document.documentElement.setAttribute('data-theme','light');
                const accent = "{{ request.user.accent_color|default:'#1f9cee' }}";
                if(accent) document.documentElement.style.setProperty('--primary', accent);
                const fs = {{ request.user.font_size|default:14 }};
                if(fs) document.documentElement.style.fontSize = fs + 'px';
            }catch(e){ /* ignore */ }
        })();
        </script>
</head>
<body>

<!-- Header -->

<header>
    <span class="toc" id="mobileTOC">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 6h16M4 12h16M4 18h16"/>
        </svg>
    </span>
    <h1 class="logo">Lupify</h1>
    <div class="search-wrapper">
        <div class="search-bar collapsed" id="mobileSearch">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input type="text" placeholder="Search Lupify...">
        </div>
    </div>
    <div class="nav-actions">
        <!-- Notifications Bell -->
        <div class="icon-btn notification-btn" id="notificationBell" style="position: relative; cursor: pointer;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-bell-icon lucide-bell">
                <path d="M10.268 21a2 2 0 0 0 3.464 0"/>
                <path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"/>
            </svg>
        </div>
        
        <div class="create-btn">Create</div>
        <div class="icon-btn avatar-wrapper">
            {% if user.avatar %}
                <img src="{{ user.avatar.url }}" class="pfp user-profile-trigger" data-user-id="{{ user.id }}" data-username="{{ user.username }}">
            {% else %}
                <div class="pfp-fallback user-profile-trigger" style="background: {{ user.color|default:'#999' }}" data-user-id="{{ user.id }}" data-username="{{ user.username }}">
                    {{ user.username|slice:":1"|upper }}
                </div>
            {% endif %}
        </div>
    </div>
</header>

<!-- Sidebar -->

<aside class="sidebar" id="sidebar">
    <div class="sidebar-logo">
        <h2>Lupify</h2>
    </div>
    <ul>
        <li class="{% if request.resolver_match.url_name == 'dashboard_home' %}active{% endif %}" title="Home">
            <a href="{% url 'dashboard_home' %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/>
                    <path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                </svg>
            </a>
        </li>
        <li class="{% if request.resolver_match.url_name == 'blogs' %}active{% endif %}" title="Blogs">
            <a href="{% url 'blogs' %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M12 7v14"/>
                    <path d="M16 12h2"/>
                    <path d="M16 8h2"/>
                    <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>
                    <path d="M6 12h2"/>
                    <path d="M6 8h2"/>
                </svg>
            </a>
        </li>
        <li class="{% if request.resolver_match.url_name == 'communities' %}active{% endif %}" title="Communities">
            <a href="{% url 'communities' %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
                </svg>
            </a>
        </li>
        <li class="{% if request.resolver_match.url_name == 'subscriptions' %}active{% endif %}" title="Subscriptions">
            <a href="{% url 'subscriptions' %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <line x1="19" x2="19" y1="8" y2="14"/>
                    <line x1="22" x2="16" y1="11" y2="11"/>
                </svg>
            </a>
        </li>
        <li title="Games">
            <a href="{% url 'games_hub' %}">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="2" y="6" width="20" height="12" rx="2"/>
                    <path d="M6 10h3v4H6z"/>
                    <path d="M15 9v6"/>
                    <path d="M18 12h-6"/>
                </svg>
            </a>
        </li>
    </ul>
</aside>

<div id="sidebarOverlay"></div>

<!-- Main wrapper -->

<div class="main-wrapper">
    {% block content %}
    <!-- Recently Played -->
    <section class="full-width" style="margin-bottom:32px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <h2 style="margin:0;font-size:1.5rem;color:var(--text-dark);">Recently Played</h2>
            <a href="{% url 'games_hub' %}" style="color:var(--primary);font-weight:500;text-decoration:none;">See all →</a>
        </div>
        <div id="recent-games" style="display:flex;gap:14px;overflow-x:auto;padding-bottom:8px;">
            {% if recent_games %}
                {% for s in recent_games %}
                    <div style="background:linear-gradient(135deg, #1f9cee15, #fec76f15);padding:16px;border-radius:12px;border:1px solid rgba(31,156,238,0.1);min-width:160px;">
                        <div style="font-weight:700;color:var(--text-dark);">{{ s.game|default:'Game' }}</div>
                        <div style="font-size:0.8rem;color:var(--secondary-text);">{{ s.last_played|date:'M d, Y' }}</div>
                    </div>
                {% endfor %}
            {% else %}
                <p style="color:var(--secondary-text);">No recent games yet. <a href="{% url 'games_hub' %}">Play now</a>!</p>
            {% endif %}
        </div>
    </section>

    <!-- Filter Bubbles -->
    <section class="full-width">
        <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px;">
            <button id="homeForYouToggle" class="filter-bubble active" type="button" data-sort="for_you">For you</button>
            <button class="filter-bubble" type="button" data-sort="latest">Latest</button>
            <button class="filter-bubble" type="button" data-sort="most_liked">Most liked</button>
            <button class="filter-bubble" type="button" data-sort="most_viewed">Most viewed</button>
            <button class="filter-bubble" type="button" data-sort="trending">Trending</button>
        </div>
    </section>

    <!-- Feed Container -->
    <div class="posts-center">
        <section id="community-feed" style="display:none;flex-direction:column;gap:14px;margin-top:8px;">
            <!-- posts loaded dynamically -->
        </section>
    </div>
    
    {% endblock %}
</div>

<!-- Create Modal -->

<div class="create-modal" id="createModal">
    <div class="modal-content">
        <h3>Select post type</h3>
        <div class="modal-options">
            <div class="modal-option" id="community-post">Community Post</div>
            <div class="modal-option" id="blog-post">Blog Post</div>
        </div>
    </div>
</div>

<form id="logout-form" method="POST" action="{% url 'logout' %}" style="display: none;">
    {% csrf_token %}
</form>

<script src="{% static 'js/dashboard.js' %}"></script>
</body>
</html>
```

---

## File: templates/marketplace/home.html
### MARKETPLACE HOME PAGE

**Purpose:** Browse and search for projects in the marketplace
**Size:** 155 lines
**Key Features:**
- Featured projects showcase
- Search functionality
- Category filtering
- Sort options (newest, popular, top rated, price)
- Project grid display with pagination

```html
{% extends "marketplace/index.html" %}
{% load static %}

{% block title %}Browse - Lupify Marketplace{% endblock %}

{% block content %}
<div class="marketplace-home">
  <!-- Hero section -->
  <section class="accent-gradient text-white py-16">
    <div class="container mx-auto px-4 text-center">
      <h1 class="text-5xl font-bold mb-4">Marketplace</h1>
      <p class="text-xl mb-8">Discover amazing projects created by talented creators</p>
      
      <!-- Search bar -->
      <form method="GET" class="max-w-2xl mx-auto">
        <div class="relative">
          <input
            type="text"
            name="q"
            value="{{ search }}"
            placeholder="Search projects..."
            class="w-full px-6 py-4 rounded-full text-gray-900 focus:outline-none focus:ring-4 focus:ring-white/50"
          />
          <button type="submit" class="absolute right-2 top-1/2 -translate-y-1/2 bg-white text-purple-600 px-6 py-2 rounded-full font-semibold hover:opacity-90">
            Search
          </button>
        </div>
      </form>
    </div>
  </section>

  <!-- Featured projects -->
  {% if featured %}
  <section class="py-12 bg-gray-50">
    <div class="container mx-auto px-4">
      <h2 class="text-3xl font-bold mb-6">Featured Projects</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for project in featured %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
          <a href="/marketplace/{{ project.slug }}/">
            <img src="{{ project.thumbnail.url }}" alt="{{ project.title }}" class="w-full h-48 object-cover">
          </a>
          <div class="p-4">
            <h3 class="font-bold text-lg mb-2">{{ project.title }}</h3>
            <p class="text-gray-600 text-sm mb-3">{{ project.short_description|truncatewords:20 }}</p>
            <div class="flex items-center justify-between">
              <span class="text-blue-600 font-bold">
                {% if project.is_free %}FREE{% else %}${{ project.price }}{% endif %}
              </span>
              <a href="/marketplace/{{ project.slug }}/" class="text-blue-600 hover:text-blue-800">
                View →
              </a>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </section>
  {% endif %}

  <!-- Filters and sorting -->
  <section class="py-8 bg-white border-b">
    <div class="container mx-auto px-4">
      <form method="GET" class="flex flex-wrap gap-4 items-center">
        <!-- Category filter -->
        <select name="category" onchange="this.form.submit()" class="px-4 py-2 rounded-lg border border-gray-300">
          <option value="">All Categories</option>
          {% for value, label in categories %}
          <option value="{{ value }}" {% if category == value %}selected{% endif %}>
            {{ label }}
          </option>
          {% endfor %}
        </select>

        <!-- Sort filter -->
        <select name="sort" onchange="this.form.submit()" class="px-4 py-2 rounded-lg border border-gray-300">
          <option value="newest" {% if sort == 'newest' %}selected{% endif %}>Newest</option>
          <option value="popular" {% if sort == 'popular' %}selected{% endif %}>Most Popular</option>
          <option value="top_rated" {% if sort == 'top_rated' %}selected{% endif %}>Top Rated</option>
          <option value="price_low" {% if sort == 'price_low' %}selected{% endif %}>Price: Low to High</option>
          <option value="price_high" {% if sort == 'price_high' %}selected{% endif %}>Price: High to Low</option>
        </select>

        <!-- Results count -->
        <span class="ml-auto text-gray-600">
          {{ projects.paginator.count }} project{{ projects.paginator.count|pluralize }}
        </span>
      </form>
    </div>
  </section>

  <!-- Projects grid -->
  <section class="py-12">
    <div class="container mx-auto px-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {% for project in projects %}
        <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-all">
          <a href="/marketplace/{{ project.slug }}/">
            <img src="{{ project.thumbnail.url }}" alt="{{ project.title }}" class="w-full h-40 object-cover">
          </a>
          <div class="p-4">
            <h3 class="font-bold text-base mb-2">{{ project.title }}</h3>
            <p class="text-gray-600 text-xs mb-3">By {{ project.creator.username }}</p>
            <div class="flex items-center justify-between">
              <span class="text-blue-600 font-bold text-sm">
                {% if project.is_free %}FREE{% else %}${{ project.price }}{% endif %}
              </span>
              <a href="/marketplace/{{ project.slug }}/" class="text-blue-600 hover:text-blue-800 text-sm">
                View
              </a>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
  </section>
</div>
{% endblock %}
```

---

## File: templates/marketplace/creator_dashboard.html
### CREATOR DASHBOARD & ANALYTICS

**Purpose:** Show creator sales, earnings, and project management
**Size:** 183 lines
**Key Features:**
- Revenue statistics
- Sales tracking
- Payout requests
- Project management
- Recent sales history

```html
{% extends "marketplace/index.html" %}
{% load static %}

{% block title %}Creator Dashboard - Marketplace{% endblock %}

{% block content %}
<div class="creator-dashboard py-8">
  <div class="container mx-auto px-4">
    <h1 class="text-4xl font-bold mb-8">Marketplace Creator Dashboard</h1>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-medium mb-2">Total Revenue</h3>
        <p class="text-4xl font-bold text-green-600">${{ total_revenue }}</p>
        <p class="text-gray-500 text-xs mt-2">All time</p>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-medium mb-2">Total Sales</h3>
        <p class="text-4xl font-bold text-blue-600">{{ total_sales }}</p>
        <p class="text-gray-500 text-xs mt-2">Projects purchased</p>
      </div>
      
      <div class="bg-white rounded-lg shadow p-6">
        <h3 class="text-gray-600 text-sm font-medium mb-2">Projects Listed</h3>
        <p class="text-4xl font-bold text-purple-600">{{ projects.count }}</p>
        <p class="text-gray-500 text-xs mt-2">In marketplace</p>
      </div>
    </div>

    <!-- Payout Section -->
    <div class="bg-white rounded-lg shadow p-6 mb-12">
      <h2 class="text-2xl font-bold mb-4">Request Payout</h2>
      <form method="POST" action="{% url 'marketplace:api_request_payout' %}" class="space-y-4">
        {% csrf_token %}
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">Amount (USD)</label>
            <input type="number" name="amount" min="10" step="0.01" value="10" required 
                   class="w-full px-4 py-2 rounded-lg border border-gray-300" />
            <p class="text-xs text-gray-500 mt-1">Minimum: $10.00</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-2">Payout Method</label>
            <select name="method" required class="w-full px-4 py-2 rounded-lg border border-gray-300">
              <option value="paypal">PayPal</option>
              <option value="bank">Bank Transfer</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium mb-2">Email</label>
            <input type="email" name="email" value="{{ user.email }}" required 
                   class="w-full px-4 py-2 rounded-lg border border-gray-300" />
          </div>
        </div>
        
        <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg">
          Request Payout
        </button>
      </form>
    </div>

    <!-- Recent Sales -->
    <div class="bg-white rounded-lg shadow p-6 mb-12">
      <h2 class="text-2xl font-bold mb-4">Recent Sales</h2>
      
      {% if recent_sales %}
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="border-b">
            <tr>
              <th class="pb-3 font-semibold">Project</th>
              <th class="pb-3 font-semibold">Buyer</th>
              <th class="pb-3 font-semibold">Amount</th>
              <th class="pb-3 font-semibold">Your Earnings</th>
              <th class="pb-3 font-semibold">Date</th>
            </tr>
          </thead>
          <tbody>
            {% for sale in recent_sales %}
            <tr class="border-b hover:bg-gray-50">
              <td class="py-3">
                <a href="/marketplace/{{ sale.project.slug }}/" class="text-blue-600 hover:underline">
                  {{ sale.project.title }}
                </a>
              </td>
              <td class="py-3">{{ sale.buyer.username }}</td>
              <td class="py-3">${{ sale.price_paid }}</td>
              <td class="py-3 text-green-600 font-semibold">${{ sale.creator_earnings }}</td>
              <td class="py-3 text-gray-500">{{ sale.completed_at|date:"M d, Y" }}</td>
            </tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
      {% else %}
      <p class="text-gray-600">No sales yet. Upload your first project!</p>
      {% endif %}
    </div>

    <!-- My Projects -->
    <div class="bg-white rounded-lg shadow p-6">
      <h2 class="text-2xl font-bold mb-4">My Projects</h2>
      
      {% if projects %}
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        {% for project in projects %}
        <div class="border rounded-lg p-4">
          <div class="flex gap-4">
            <img src="{{ project.thumbnail.url }}" alt="{{ project.title }}" class="w-24 h-24 object-cover rounded">
            <div class="flex-1">
              <h3 class="font-bold mb-2">{{ project.title }}</h3>
              
              <div class="text-sm space-y-1 mb-3">
                <p><span class="text-gray-600">Status:</span> 
                  <span class="inline-block px-2 py-1 rounded text-xs font-semibold {% if project.status == 'approved' %}bg-green-100 text-green-800{% elif project.status == 'pending_review' %}bg-yellow-100 text-yellow-800{% else %}bg-red-100 text-red-800{% endif %}">
                    {{ project.get_status_display }}
                  </span>
                </p>
                <p><span class="text-gray-600">Views:</span> {{ project.views_count }}</p>
                <p><span class="text-gray-600">Sales:</span> {{ project.total_sales }} (${{ project.total_revenue|default:0 }})</p>
              </div>
              
              <div class="flex gap-2">
                <a href="/marketplace/{{ project.slug }}/" class="text-blue-600 hover:underline text-sm">View</a>
                <a href="/marketplace/{{ project.slug }}/edit/" class="text-blue-600 hover:underline text-sm">Edit</a>
              </div>
            </div>
          </div>
        </div>
        {% endfor %}
      </div>
      {% else %}
      <p class="text-gray-600 mb-4">You haven't uploaded any projects yet.</p>
      {% endif %}
      
      <div class="mt-6">
        <a href="{% url 'marketplace:upload' %}" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">
          Upload New Project
        </a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## File: templates/games/dashboard.html
### GAMES EDITOR DASHBOARD

**Purpose:** Manage and edit games, track analytics
**Size:** 501 lines
**Key Features:**
- Game list management
- Analytics and statistics
- New game creation
- Game editor launch
- Performance charts
- Help system

```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Game Editor Dashboard</title>
  <link rel="stylesheet" href="{% static 'css/dashboard.css' %}">
  <style>
    :root{--bg:#0f1720;--card:#0b1220;--muted:#9aa4b2;--accent:#1f9cee;--text:#e6eef6;--border:rgba(31,156,238,0.1)}
    [data-theme='light']{--bg:#f6f8fb;--card:#fff;--text:#222;--muted:#666;--border:rgba(31,156,238,0.15)}
    *{margin:0;padding:0;box-sizing:border-box}
    body{background:var(--bg);color:var(--text);font-family:'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif;line-height:1.5}
    .container{max-width:1200px;margin:0 auto;padding:0 24px}
    
    /* Topbar */
    .topbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:32px;padding-top:24px;position:relative;z-index:1}
    .back-btn{background:transparent;border:none;color:var(--accent);cursor:pointer;font-size:28px;padding:8px;border-radius:8px;transition:all .2s;display:flex;align-items:center}
    .back-btn:hover{background:rgba(31,156,238,0.08);transform:translateX(-2px)}
    .topbar-title{flex:1;display:flex;align-items:center;gap:16px}
    .topbar-title h1{margin:0;font-size:28px;font-weight:700}
    .topbar-actions{display:flex;gap:10px;align-items:center}
    
    /* Buttons */
    .btn{background:var(--accent);color:#fff;padding:10px 16px;border-radius:8px;border:none;cursor:pointer;font-weight:600;transition:all .2s;font-size:14px}
    .btn:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(31,156,238,0.3)}
    .help-btn{background:rgba(31,156,238,0.1);color:var(--accent);width:32px;height:32px;border-radius:50%;border:none;cursor:pointer;font-weight:700;transition:all .2s;display:flex;align-items:center;justify-content:center}
    
    /* Layout */
    .layout{display:grid;grid-template-columns:1fr 360px;gap:20px;margin-bottom:40px;}
    .panel{background:var(--card);border-radius:12px;padding:20px;box-shadow:0 4px 16px rgba(0,0,0,0.3);border:1px solid var(--border);}
    .panel h3{margin:0 0 16px;font-size:18px;font-weight:700;color:var(--text)}
    
    /* Game List */
    .list{display:flex;flex-direction:column;gap:12px;max-height:580px;overflow-y:auto;}
    .game-row{display:flex;gap:12px;align-items:center;padding:12px;border-radius:10px;border:1px solid transparent;transition:all .2s;background:rgba(255,255,255,0.01);}
    .game-row:hover{transform:translateY(-3px);box-shadow:0 8px 20px rgba(31,156,238,0.15);border-color:var(--accent)}
    
    .thumb{width:80px;height:54px;background:#08101a;border-radius:8px;flex:0 0 80px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:12px;overflow:hidden;border:1px solid var(--border)}
    .thumb img{width:100%;height:100%;object-fit:cover}
    
    .meta{flex:1;display:flex;flex-direction:column;gap:4px}
    .title{font-weight:700;font-size:15px;color:var(--text)}
    .metrics{display:flex;gap:12px;color:var(--muted);font-size:12px;flex-wrap:wrap}
    
    /* Stats */
    .stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}
    .stat{background:rgba(31,156,238,0.05);padding:14px;border-radius:10px;text-align:center;border:1px solid var(--border);}
    .stat > div{font-size:20px;font-weight:700;color:var(--accent);margin-bottom:4px}
    .stat small{color:var(--muted);font-size:12px}
    
    /* Modal */
    .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.6);display:none;align-items:center;justify-content:center;z-index:2000;backdrop-filter:blur(2px)}
    .modal-overlay.show{display:flex}
    .modal-content{background:var(--card);border-radius:12px;padding:24px;max-width:560px;width:90%;border:1px solid var(--border);}
    
    @media(max-width:980px){.layout{grid-template-columns:1fr}.stats-grid{grid-template-columns:repeat(2,1fr)}}
    @media(max-width:640px){.container{padding:0 16px}.topbar{flex-direction:column;gap:12px;align-items:flex-start}.stats-grid{grid-template-columns:1fr}}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body data-theme="dark">
  <div class="container">
    <div class="topbar">
      <div class="topbar-title">
        <button class="back-btn" id="backBtn" title="Return to dashboard">←</button>
        <h1>Game Editor</h1>
      </div>
      <div class="topbar-actions">
        <button class="help-btn" id="helpBtn" title="Show help">?</button>
        <button id="newGameBtn" class="btn">New Game</button>
      </div>
    </div>

    <!-- Stats -->
    <div class="stats-grid">
      <div class="stat">
        <div>{{ games_count }}</div>
        <small>Games Created</small>
      </div>
      <div class="stat">
        <div>{{ total_plays }}</div>
        <small>Total Plays</small>
      </div>
      <div class="stat">
        <div>{{ avg_rating|default:"—" }}</div>
        <small>Avg Rating</small>
      </div>
      <div class="stat">
        <div>{{ total_downloads }}</div>
        <small>Downloads</small>
      </div>
    </div>

    <!-- Main layout -->
    <div class="layout">
      <!-- Games list (main) -->
      <div class="panel">
        <h3>Your Games</h3>
        <div class="list" id="gamesList">
          <!-- Games will be loaded here -->
        </div>
      </div>

      <!-- Recent activity (sidebar) -->
      <div class="panel">
        <h3>Recent Activity</h3>
        <div id="activityList" style="font-size:12px;color:var(--muted);max-height:580px;overflow-y:auto;">
          <p>No recent activity</p>
        </div>
      </div>
    </div>
  </div>

  <!-- New Game Modal -->
  <div class="modal-overlay" id="newGameModal">
    <div class="modal-content">
      <h2 style="margin-bottom:16px;color:var(--text)">Create New Game</h2>
      <form id="newGameForm">
        <div style="margin-bottom:12px;">
          <label style="display:block;margin-bottom:6px;font-weight:600;color:var(--text);">Game Name</label>
          <input type="text" name="name" placeholder="My Awesome Game" style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:rgba(255,255,255,0.05);color:var(--text);" required>
        </div>
        <div style="margin-bottom:12px;">
          <label style="display:block;margin-bottom:6px;font-weight:600;color:var(--text);">Description</label>
          <textarea name="description" placeholder="Describe your game..." style="width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:rgba(255,255,255,0.05);color:var(--text);resize:vertical;min-height:80px;"></textarea>
        </div>
        <div style="display:flex;gap:12px;justify-content:flex-end;margin-top:20px;">
          <button type="button" id="cancelGameBtn" style="padding:10px 16px;border-radius:8px;border:1px solid var(--border);background:transparent;color:var(--text);cursor:pointer;font-weight:600;">Cancel</button>
          <button type="submit" style="padding:10px 16px;border-radius:8px;border:none;background:var(--accent);color:#fff;cursor:pointer;font-weight:600;">Create</button>
        </div>
      </form>
    </div>
  </div>

  <script src="{% static 'js/dashboard.js' %}"></script>
</body>
</html>
```

---

# 🎨 STYLESHEET FILES

## File: static/css/dashboard.css
### MAIN DASHBOARD STYLES

**Size:** 751 lines
**Key Features:**
- Color schemes (light/dark mode)
- Header & navigation styling
- Sidebar styling
- Feed cards and posts
- Responsive layout
- Animations & transitions

**Top Section (CSS Variables & Base):**
```css
:root {
    --primary: #1f9cee;
    --primary-dark: #167ac6;
    --accent: #fec76f;
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --text-dark: #111827;
    --secondary-text: #6b7280;
    --icon-default: #6b7280;
    --card-shadow: 0 6px 18px rgba(0,0,0,0.05);
}

html[data-theme="dark"] {
    --primary: #bb86fc;
    --primary-dark: #9c27b0;
    --accent: #fec76f;
    --bg: #121212;
    --card-bg: #1e1e1e;
    --text-dark: #ffffff;
    --secondary-text: #b0b0b0;
    --icon-default: #b0b0b0;
    --card-shadow: 0 6px 18px rgba(0,0,0,0.3);
}

/* Base Body */
body {
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    background: var(--bg);
    color: var(--text-dark);
    overflow-x: hidden;
}

/* Header */
header {
    background: var(--card-bg);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1200;
    height: 80px;
}

.logo {
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--primary);
    min-width: 120px;
    margin-right: 20px;
}

.search-bar {
    width: 60%;
    max-width: 550px;
    display: flex;
    align-items: center;
    background: var(--card-bg);
    border: 2px solid var(--primary);
    border-radius: 50px;
    padding: 8px 14px;
    transition: all 0.3s ease;
}

.search-bar input {
    flex: 1;
    border: none;
    background: transparent;
    color: var(--text-dark);
    outline: none;
    font-size: 0.95rem;
}

/* Sidebar */
.sidebar {
    position: fixed;
    left: 0;
    top: 80px;
    width: 100px;
    height: calc(100vh - 80px);
    background: var(--card-bg);
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 20px 0;
    border-right: 1px solid rgba(0, 0, 0, 0.1);
    z-index: 1100;
}

.sidebar ul {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 20px;
    width: 100%;
    padding: 0;
}

.sidebar li {
    display: flex;
    justify-content: center;
}

.sidebar li a {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    color: var(--secondary-text);
    transition: all 0.3s ease;
}

.sidebar li a svg {
    width: 24px;
    height: 24px;
    stroke: currentColor;
}

.sidebar li.active a {
    background: var(--primary);
    color: white;
}

.sidebar li a:hover {
    background: var(--primary);
    color: white;
}

/* Main wrapper */
.main-wrapper {
    margin-left: 100px;
    margin-top: 80px;
    padding: 20px;
}

/* Filter bubbles */
.filter-bubble {
    padding: 8px 16px;
    border-radius: 20px;
    border: 2px solid var(--primary);
    background: transparent;
    color: var(--primary);
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s ease;
    font-size: 0.9rem;
}

.filter-bubble:hover {
    background: var(--primary);
    color: white;
}

.filter-bubble.active {
    background: var(--primary);
    color: white;
}

/* Posts container */
.posts-center {
    display: flex;
    flex-direction: column;
    gap: 14px;
    max-width: 600px;
    margin: 0 auto;
}

/* Responsive */
@media (max-width: 1024px) {
    .main-wrapper {
        margin-left: 0;
    }
    
    .sidebar {
        display: none;
    }
    
    .sidebar.open {
        display: flex;
    }
}

@media (max-width: 640px) {
    .search-bar {
        width: 100%;
        max-width: none;
    }
    
    header {
        flex-wrap: wrap;
        height: auto;
        padding: 8px 12px;
    }
    
    .main-wrapper {
        padding: 12px;
    }
}
```

---

## File: static/js/dashboard.js
### DASHBOARD JAVASCRIPT

**Size:** Variable (handles dynamic loading)
**Key Functions:**
- Filter bubble clicks (sort/filter posts)
- Modal handling (create post, interests)
- API calls for posts/recommendations
- Theme switching
- User profile menu
- Notification system
- Create button functionality

**Key Code Structure:**
```javascript
// Theme initialization
(function initTheme() {
    const serverTheme = document.querySelector('meta[name="theme"]')?.content || 'light';
    document.documentElement.setAttribute('data-theme', serverTheme);
})();

// Filter bubble handlers
document.querySelectorAll('.filter-bubble').forEach(btn => {
    btn.addEventListener('click', function() {
        // Remove active from all
        document.querySelectorAll('.filter-bubble').forEach(b => b.classList.remove('active'));
        // Add active to clicked
        this.classList.add('active');
        
        const sort = this.dataset.sort;
        loadPosts(sort);
    });
});

// Load posts dynamically
async function loadPosts(sortBy) {
    try {
        const response = await fetch(`/dashboard/community-posts-api/?sort=${sortBy}`);
        const data = await response.json();
        
        const feedContainer = document.getElementById('community-feed');
        feedContainer.innerHTML = '';
        
        data.posts.forEach(post => {
            feedContainer.appendChild(createPostElement(post));
        });
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

// Create post modal
document.getElementById('createModal')?.addEventListener('click', function(e) {
    if (e.target.id === 'community-post') {
        window.location.href = '/communities/create-post/';
    } else if (e.target.id === 'blog-post') {
        window.location.href = '/posts/create/';
    }
});

// Notification bell
document.getElementById('notificationBell')?.addEventListener('click', function() {
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
});

// Logout
document.getElementById('logout')?.addEventListener('click', function() {
    document.getElementById('logout-form').submit();
});
```

---

# 📚 TEMPLATE STRUCTURE SUMMARY

## Template Inheritance Hierarchy

```
base.html (main base template)
├── dashboardhome.html (user dashboard)
├── index.html (home page)
└── marketplace/index.html (marketplace base)
    ├── home.html (marketplace home)
    ├── creator_dashboard.html (creator stats)
    ├── project_detail.html (project page)
    ├── upload.html (upload page)
    └── library.html (user library)
```

## Key Template Blocks

All templates extend `base.html` or specific app bases:
- `{% block title %}` - Page title
- `{% block content %}` - Main page content
- `{% block extra_css %}` - Additional stylesheets
- `{% block extra_js %}` - Additional scripts

## Django Template Tags Used

```django
{% load static %}              - Load static files
{% url 'name' %}              - Reverse URLs
{% if condition %}            - Conditionals
{% for item in list %}        - Loops
{{ variable }}                - Display variables
{{ variable|filter }}         - Filters
{% csrf_token %}              - CSRF protection
```

---

# 🔧 HOW TO CUSTOMIZE

## To Add New Dashboard Cards:
1. Edit `templates/dashboardhome.html`
2. Add new `<section>` with class `full-width`
3. Add corresponding JavaScript in `static/js/dashboard.js`

## To Style New Elements:
1. Add CSS to `static/css/dashboard.css`
2. Use CSS variables like `var(--primary)`, `var(--bg)`, etc.
3. Include media queries for responsive design

## To Add New Pages:
1. Create template file
2. Add view function in app views.py
3. Add URL pattern in app urls.py
4. Link in navigation

---

**Last Updated:** December 13, 2025
**Template Engine:** Django 4.2
**CSS Framework:** Custom + Tailwind utilities
