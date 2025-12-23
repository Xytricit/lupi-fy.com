# Dashboard Template Blocks Reference

The `dashboardhome.html` template now includes Django template blocks for easy customization and extension.

## Available Blocks

### **Head Section Blocks**

#### `{% block title %}`
- **Default**: "Lupify - Social Gaming Dashboard"
- **Purpose**: Page title displayed in browser tab
- **Example**:
```django
{% block title %}My Custom Dashboard - Lupify{% endblock %}
```

#### `{% block meta_description %}`
- **Default**: "Lupify - Your Gaming Community Hub"
- **Purpose**: SEO meta description
- **Example**:
```django
{% block meta_description %}Discover amazing games and connect with gamers{% endblock %}
```

#### `{% block og_title %}`
- **Default**: "Lupify - Social Gaming Dashboard"
- **Purpose**: Open Graph title for social media sharing
- **Example**:
```django
{% block og_title %}Custom Page Title for Social Share{% endblock %}
```

#### `{% block og_description %}`
- **Default**: "Connect, play, and share with the gaming community"
- **Purpose**: Open Graph description for social media
- **Example**:
```django
{% block og_description %}Join our gaming community today!{% endblock %}
```

#### `{% block extra_head %}`
- **Default**: Empty
- **Purpose**: Add custom CSS, meta tags, or scripts in the `<head>`
- **Example**:
```django
{% block extra_head %}
<link rel="stylesheet" href="{% static 'css/custom.css' %}">
<script src="{% static 'js/analytics.js' %}"></script>
{% endblock %}
```

---

### **Body Section Blocks**

#### `{% block body_content %}`
- **Purpose**: Wraps all body content (header, sidebar, main, scripts)
- **Use Case**: Complete page override while keeping base HTML structure
- **Example**:
```django
{% block body_content %}
<div class="custom-layout">
    <!-- Completely custom layout -->
</div>
{% endblock %}
```

#### `{% block header %}`
- **Purpose**: Customize or replace the entire header section
- **Includes**: Logo, search bar, notifications, profile menu
- **Example**:
```django
{% block header %}
<header class="custom-header">
    <!-- Custom header content -->
</header>
{% endblock %}
```

#### `{% block sidebar %}`
- **Purpose**: Customize or replace the sidebar navigation
- **Includes**: Home, Blogs, Communities, Subscriptions, Games, Marketplace links
- **Example**:
```django
{% block sidebar %}
<aside class="custom-sidebar">
    <!-- Custom navigation -->
</aside>
{% endblock %}
```

#### `{% block main_content %}`
- **Purpose**: Main content area (games, feed, filters)
- **Default**: Recently Played section + Feed container
- **Example**:
```django
{% block main_content %}
<div class="container">
    <h1>Custom Dashboard Content</h1>
    <!-- Your content -->
</div>
{% endblock %}
```

#### `{% block fab_button %}`
- **Purpose**: Floating Action Button (Create post)
- **Default**: Button linking to create community post
- **Example**:
```django
{% block fab_button %}
<button class="fab" onclick="customAction()">
    <svg>...</svg>
</button>
{% endblock %}
```

---

### **Script Blocks**

#### `{% block scripts %}`
- **Purpose**: Main JavaScript block with all dashboard functionality
- **Includes**: Search, feed loading, interaction tracking, etc.
- **Example**:
```django
{% block scripts %}
{{ block.super }}  {# Include parent scripts #}
<script>
    // Additional custom scripts
</script>
{% endblock %}
```

#### `{% block extra_scripts %}`
- **Default**: Empty
- **Purpose**: Add additional scripts after main scripts load
- **Example**:
```django
{% block extra_scripts %}
<script src="{% static 'js/custom-dashboard.js' %}"></script>
{% endblock %}
```

---

## Usage Examples

### **Extending the Dashboard**

```django
{% extends "dashboardhome.html" %}

{% block title %}Creator Dashboard - Lupify{% endblock %}

{% block main_content %}
<div class="container">
    <h1>Creator Analytics</h1>
    <div class="stats-grid">
        <!-- Custom creator content -->
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
    // Custom creator dashboard scripts
</script>
{% endblock %}
```

### **Adding Custom Styles**

```django
{% extends "dashboardhome.html" %}

{% block extra_head %}
<style>
    .custom-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
    }
</style>
{% endblock %}
```

### **Overriding Header Only**

```django
{% extends "dashboardhome.html" %}

{% block header %}
<header class="custom-header">
    <div class="logo">My Custom Logo</div>
    <nav>
        <!-- Custom navigation -->
    </nav>
</header>
{% endblock %}
```

---

## Block Hierarchy

```
body_content
├── header
├── sidebar
├── main_content
├── fab_button
├── scripts
└── extra_scripts
```

---

## Tips

1. **Use `{{ block.super }}`** to include parent block content:
   ```django
   {% block scripts %}
   {{ block.super }}
   <script>/* Your additional code */</script>
   {% endblock %}
   ```

2. **Keep CSS in extra_head** for custom styling without overriding base styles

3. **Use extra_scripts** for page-specific JavaScript that depends on base scripts

4. **Override main_content** for custom dashboard layouts while keeping header/sidebar

5. **Test responsive behavior** when overriding header or sidebar blocks
