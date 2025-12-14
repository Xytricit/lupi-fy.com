# Dashboard JavaScript (static/js/dashboard.js)

## File Overview
**Path:** `static/js/dashboard.js`  
**Size:** 1180 lines  
**Purpose:** Complete dashboard interactivity - theme switching, modals, recommendations, dropdowns, search

---

## Core Handlers & Features

### 1. Theme Handler (Lines 5-78)
Manages light/dark/system theme preference with localStorage persistence

**Key Functions:**
- `systemApplyListener()` - Listens to OS theme changes
- `scheduleTimeFallback()` - Fallback for systems without matchMedia
- `persistPreference()` - Saves theme to backend
- `applyChoice()` - Applies selected theme
- `window.applyThemeChoice()` - Public API for theme switching

**Features:**
- ✅ System preference detection
- ✅ Time-based fallback (7am-7pm light, rest dark)
- ✅ localStorage backup
- ✅ Backend persistence to database
- ✅ Real-time theme switching buttons in avatar menu

---

### 2. Avatar Menu Dropdown (Lines 81-123)
Separate dropdown from profile popup - contains theme options

**Handlers:**
- Click on avatar wrapper toggles menu
- Click outside closes menu
- Theme buttons update preference and persist

**Elements:**
- `.avatar-wrapper` - Container
- `.avatar-menu` - Dropdown element
- `.theme-option` buttons - Theme selection

---

### 3. Notifications Bell & Dropdown (Lines 126-196)
Real-time notification loading and display

**Key Functions:**
- `loadNotifications(limit)` - Fetches from `/notifications/api/recent/`
- Badge updates with unread count
- Click opens/closes dropdown
- Click outside closes dropdown

**API Endpoint:** `/notifications/api/recent/?limit=6`

**Response Format:**
```json
{
  "notifications": [
    {
      "id": 123,
      "title": "New notification",
      "message": "Content preview",
      "url": "/target-page/",
      "unread": true
    }
  ]
}
```

---

### 4. Logout Handler (Lines 199-204)
Submits logout form when button clicked

**Elements:**
- `#logout` button
- `#logout-form` form element

---

### 5. Create Modal (Lines 207-233)
Opens modal to choose post type (blog or community)

**Handlers:**
- `.create-btn` click opens modal
- Modal close on background click
- `#blog-post` button navigates to `/posts/create/`
- `#community-post` button navigates to `/community/create/`

**Modal Elements:**
- `#createModal` - Modal container
- `#blog-post` - Blog post button
- `#community-post` - Community post button

---

### 6. Onboarding Interests (Lines 236-396)
3-step onboarding flow for game/blog/community preferences

**Steps:**
1. Game category selection (`#interestsModal`)
2. Blog tags selection (`#blogTagsModal`)
3. Community tags selection (`#communityTagsModal`)

**Functions:**
- `getCSRF()` - Extracts CSRF token from cookies/DOM
- `loadTagOptions()` - Fetches available tags
- `makeChipSelectionHandler()` - Handles chip selection/deselection
- `checkOnboardingStatus()` - Checks which steps completed

**API Endpoints:**
- `GET /recommend/tag-options/?type=blog` - Get available tags
- `GET /recommend/interests/` - Check completion status
- `POST /recommend/interests/save/` - Save selections

**Request Format:**
```json
{
  "type": "game|blog|community",
  "items": ["slug1", "slug2"]
}
```

---

### 7. Recommendations (Lines 399-690)
Loads and displays personalized recommendations

**Main Functions:**
- `loadAllRecommendations()` - Loads all recommendation types
- `loadForYouRecommendations()` - Personalized "for you" content
- `loadBlogRecommendations()` - Blog-specific recommendations
- `loadCommunityRecommendations()` - Community post recommendations

**API Endpoints:**
- `GET /recommend/for-you/` - All types recommendations
- `GET /recommend/blog-recommendations/` - Blog articles
- `GET /recommend/community-recommendations/` - Community posts

**Community Post Card Features:**
- Community & author avatars with clickable links
- Image with fallback
- Like/dislike buttons with counts
- Comment link
- Bookmark toggle
- Share & report menu (ellipsis)
- Hover animation

---

### 8. Search Bar (Lines 693-722)
Mobile-responsive search with input expansion

**Handlers:**
- Click search icon toggles expanded state
- Click outside collapses
- Input focus on expand
- Hides nav actions on mobile during search

**Elements:**
- `#mobileSearch` - Container
- `input` - Search field
- `svg` - Search icon

**CSS Classes:**
- `.expanded` - Search bar wide
- `.collapsed` - Search bar icon-only
- `.hide-on-search` - Hide nav actions

---

### 9. Sidebar Mobile (Lines 725-754)
Mobile hamburger menu toggle

**Handlers:**
- `#mobileTOC` button opens/closes sidebar
- Overlay click closes sidebar
- Window resize auto-closes on desktop

**Elements:**
- `#sidebar` - Sidebar container
- `#sidebarOverlay` - Overlay background
- `#mobileTOC` - Hamburger button

**CSS Classes:**
- `.mobile` - Applied on small screens
- `.active` - Sidebar open/visible

---

### 10. Create Button Modal (Lines 757-773)
Alternative handler for create button (backup)

---

### 11. Notification Bell Dropdown (Lines 776-783)
Alternative handler for notification dropdown (backup)

---

### 12. User Avatar Menu Dropdown (Lines 786-803)
Profile menu dropdown for Profile, Appearance, Account, Creator links

**Handlers:**
- `.user-profile-trigger` click toggles dropdown
- `#logout` button submits form

**Elements:**
- `.user-profile-trigger` - Avatar/menu button
- `#userMenuDropdown` - Dropdown container

---

### 13. Global Dropdown Close Handler (Lines 806-825)
Ensures only one dropdown open at a time

Monitors clicks and closes non-relevant dropdowns

---

### 14. Filter Bubbles & Community Posts (Lines 828-877)
Dynamic post loading with filter selection

**Handlers:**
- `.filter-bubble` click sets sort type and loads posts
- `async loadCommunityPosts(sort)` fetches from API

**API Endpoint:** `GET /dashboard/community-posts-api/?sort=for_you|latest|most_liked`

**Post Card Structure:**
- Author avatar + name (clickable)
- Title
- Content preview
- Like button
- View post link

**Function:** `createPostCard(post)` - Renders individual post cards

---

### 15. Search Functionality (Lines 880-936)
Search suggestions dropdown with debouncing

**Key Functions:**
- Debounced input listener (300ms delay)
- `showSearchSuggestions(suggestions)` - Renders dropdown
- `hideSuggestions()` - Closes dropdown
- Click outside closes

**API Endpoint:** `GET /dashboard/search-suggestions/?q=query`

**Response Format:**
```json
{
  "suggestions": [
    {
      "title": "Result title",
      "url": "/target-page/",
      "type": "blog|community|game",
      "category": "Category name"
    }
  ]
}
```

---

### 16. CSS Spinner Animation (Lines 939-950)
Injects @keyframes spin for loading states

**Usage:** Applied to loading spinners in recommendations and filters

---

## Event Listeners Summary

| Element | Event | Handler |
|---------|-------|---------|
| `.create-btn` | click | Opens create modal |
| `#createModal` | click | Close on background |
| `#blog-post` | click | Navigate to blog creation |
| `#community-post` | click | Navigate to community creation |
| `#notificationBell` | click | Toggle notification dropdown |
| `#logout` | click | Submit logout form |
| `.filter-bubble` | click | Load community posts by sort |
| `#searchInput` | input | Show search suggestions |
| `#mobileTOC` | click | Toggle mobile sidebar |
| `.avatar-wrapper` | click | Toggle avatar menu |
| `.user-profile-trigger` | click | Toggle user menu dropdown |
| `document` | click | Close dropdowns on outside click |

---

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/accounts/appearance/` | POST | Save theme preference |
| `/notifications/api/recent/` | GET | Load recent notifications |
| `/recommend/tag-options/` | GET | Get available interest tags |
| `/recommend/interests/` | GET | Check onboarding status |
| `/recommend/interests/save/` | POST | Save interest selections |
| `/recommend/for-you/` | GET | Get personalized recommendations |
| `/recommend/blog-recommendations/` | GET | Get blog recommendations |
| `/recommend/community-recommendations/` | GET | Get community post recommendations |
| `/dashboard/community-posts-api/` | GET | Get posts by sort filter |
| `/dashboard/search-suggestions/` | GET | Get search suggestions |
| `/communities/api/post/{id}/like/` | POST | Like post |
| `/communities/api/post/{id}/dislike/` | POST | Dislike post |
| `/communities/api/post/{id}/bookmark/` | POST | Bookmark post |
| `/communities/api/post/{id}/report/` | POST | Report post |

---

## Key CSS Variables Used

```javascript
var(--primary)            // Primary color (accent)
var(--secondary-text)     // Secondary text color
var(--card-bg)           // Card background
var(--text-dark)         // Dark text color
var(--border-color)      // Border color
var(--bg)                // Main background
var(--danger)            // Danger/error color
var(--hover-bg)          // Hover state background
var(--muted-bg)          // Muted background
```

---

## Helper Functions

**`getCSRF()`**
Extracts CSRF token from cookies or DOM for POST requests

**`csrfToken()`** (referenced but not defined in file)
Assumes global function or utility for CSRF extraction

---

## Important Notes

1. **Theme Persistence:** Saves to both localStorage and database
2. **Notifications:** Requires API endpoint returning notifications JSON
3. **Recommendations:** Requires recommendation engine backend
4. **Mobile Responsive:** All handlers check viewport width
5. **Search Debouncing:** 300ms delay to reduce API calls
6. **Dropdown Management:** Global click listener prevents multiple open dropdowns
7. **Error Handling:** Try-catch blocks on all fetch operations
8. **CSRF Protection:** All POST requests include CSRF token

---

## Required DOM Elements

For full functionality, templates must include:
- `#createModal` - Create post modal
- `#notificationBell` - Notification bell button
- `#notificationDropdown` - Notification dropdown
- `#sidebar` - Main sidebar
- `#mobileTOC` - Mobile hamburger button
- `#sidebarOverlay` - Sidebar overlay
- `.avatar-wrapper` - Avatar dropdown wrapper
- `.avatar-menu` - Avatar dropdown menu
- `#userMenuDropdown` - User profile dropdown
- `#searchInput` - Search input field
- `.filter-bubble` - Filter toggle buttons
- `#community-feed` - Community posts container
- `[data-theme-pref]` - Meta tag with theme preference
- `#logout-form` - Logout form element
