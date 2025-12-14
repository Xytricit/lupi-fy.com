# 🧪 TESTING GUIDE - LUPIFY CORRECTIONS

**Server Running At:** http://127.0.0.1:8000/  
**Status:** ✅ Ready for Testing

---

## 📋 Manual Testing Checklist

### **Test 1: Mobile Menu (Hamburger)**

**How to Test:**
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Set width to 768px or less
4. Look for hamburger menu icon (☰) in top-left
5. Click it

**Expected Result:** ✅
- Sidebar slides in from left
- Dark overlay appears behind sidebar
- Click overlay to close sidebar
- Sidebar matches screen height

**If PASSES:** ✅ Mobile Menu Working

---

### **Test 2: Create Button**

**How to Test:**
1. Look for "Create" button in header
2. Click it

**Expected Result:** ✅
- Modal appears in center of screen
- "Select post type" heading shows
- Two options: "Community Post" and "Blog Post"
- Click outside modal to close

**If PASSES:** ✅ Create Modal Working

---

### **Test 3: Search Bar**

**How to Test:**
1. Click search bar
2. Type a letter (e.g., "t")
3. Wait 300ms

**Expected Result:** ✅
- Search suggestions dropdown appears
- Shows multiple result items
- Each item has title and type
- Items have hover effect
- Click outside to close

**If PASSES:** ✅ Search Working

---

### **Test 4: Notification Bell**

**How to Test:**
1. Look for bell icon 🔔 in header
2. Click it

**Expected Result:** ✅
- Dropdown menu appears below bell
- Header: "Recent Notifications"
- "More" link to notifications page
- Notification list area
- Close on click outside

**If PASSES:** ✅ Notifications Working

---

### **Test 5: User Avatar Menu**

**How to Test:**
1. Look for user avatar/profile pic in top-right
2. Click on it

**Expected Result:** ✅
- Dropdown menu appears below avatar
- Shows username and email
- Links to: Profile, Appearance, Account, Creator Dashboard
- Logout button in red at bottom
- Each item has hover effect
- Close on click outside

**If PASSES:** ✅ User Menu Working

---

### **Test 6: Filter Bubbles**

**How to Test:**
1. Go to /dashboard/
2. Look for filter bubbles: "For you", "Latest", etc.
3. Click different bubbles

**Expected Result:** ✅
- Clicked bubble highlights (becomes active)
- Loading spinner appears in feed
- Posts load dynamically
- Different posts show per filter
- No page reload needed
- Smooth fade-in of posts

**If PASSES:** ✅ Filter Bubbles Working

---

### **Test 7: Marketplace Links**

**How to Test:**
1. Go to /marketplace/
2. Click on any project card/link
3. Check URL in address bar

**Expected Result:** ✅
- URL shows: `/marketplace/[project-slug]/`
- NOT: `/marketplace/[slug]/` with hardcoded path
- Project detail page loads
- No 404 errors

**If PASSES:** ✅ Marketplace URLs Fixed

---

### **Test 8: Creator Dashboard Links**

**How to Test:**
1. Go to /marketplace/creator/
2. Look at "My Projects" section
3. Click "View" or "Edit" on a project

**Expected Result:** ✅
- "View" takes to project detail page
- "Edit" takes to project edit page
- URLs are properly resolved
- No errors in console

**If PASSES:** ✅ Creator Dashboard URLs Fixed

---

### **Test 9: Dropdowns Close on Click Outside**

**How to Test:**
1. Open any dropdown (search, notifications, user menu)
2. Click somewhere else on page
3. Dropdown should close

**Expected Result:** ✅
- Dropdown closes immediately
- No errors in console
- Other dropdowns don't affect this one

**If PASSES:** ✅ Dropdown Logic Working

---

### **Test 10: Mobile Sidebar Animation**

**How to Test:**
1. Resize to mobile (≤768px)
2. Click hamburger (☰)
3. Watch sidebar slide in
4. Click overlay
5. Watch sidebar slide out

**Expected Result:** ✅
- Smooth slide-in animation (0.3s)
- Dark overlay fades in
- Smooth slide-out animation
- No jank or stuttering
- All at 60fps

**If PASSES:** ✅ Mobile Animations Working

---

## 🔍 Browser Console Testing

### **Check for JavaScript Errors:**

```javascript
// Open DevTools Console (F12)
// Look for red error messages
// Should see ZERO errors

// You should see only normal info/warnings
```

### **Check Performance:**

```javascript
// Open DevTools Performance tab
// Do the following:
1. Click filter bubble
2. Type in search
3. Click dropdown buttons
4. Watch for FPS drops

// All should run at 60fps
```

---

## 📱 Responsive Testing

### **Desktop (1920x1080):**
- [ ] All dropdowns visible and clickable
- [ ] Search suggestions align properly
- [ ] Sidebar visible on left
- [ ] Hamburger menu NOT visible
- [ ] All content fits on screen

### **Tablet (768x1024):**
- [ ] Mobile menu appears (hamburger)
- [ ] Sidebar hidden by default
- [ ] Sidebar slides in on click
- [ ] Overlay appears
- [ ] Content responsive

### **Mobile (375x667):**
- [ ] Everything still works
- [ ] Touch targets are big enough
- [ ] No horizontal scroll
- [ ] Text readable
- [ ] Dropdowns don't go off-screen

---

## 🐛 Troubleshooting

### **If Dropdowns Don't Open:**
- [ ] Check browser console for errors (F12)
- [ ] Clear browser cache (Ctrl+Shift+Delete)
- [ ] Hard reload page (Ctrl+Shift+R)
- [ ] Check if JavaScript is enabled

### **If Search Doesn't Work:**
- [ ] Type at least 2 characters
- [ ] Wait 300ms for suggestions to appear
- [ ] Check network tab for API calls
- [ ] Verify /dashboard/search-suggestions/ endpoint exists

### **If Filter Bubbles Don't Load Posts:**
- [ ] Check console for errors
- [ ] Verify /dashboard/community-posts-api/ endpoint exists
- [ ] Check API returns JSON format
- [ ] Verify user is logged in

### **If Mobile Menu Doesn't Work:**
- [ ] Reduce browser width to ≤768px
- [ ] Look for hamburger icon (☰)
- [ ] Check if JavaScript is loading (Network tab)
- [ ] Check console for errors

---

## ✅ Full Test Checklist

| Test | Status | Notes |
|------|--------|-------|
| Mobile Menu | ⭕ | Click hamburger |
| Create Button | ⭕ | Opens modal |
| Search | ⭕ | Type to see suggestions |
| Notifications | ⭕ | Click bell icon |
| User Menu | ⭕ | Click avatar |
| Filter Bubbles | ⭕ | Posts load dynamically |
| Marketplace Links | ⭕ | No hardcoded paths |
| Creator Dashboard | ⭕ | Links work |
| Click Outside Close | ⭕ | Dropdowns close |
| Mobile Animation | ⭕ | Smooth 0.3s |
| Desktop Layout | ⭕ | Hamburger hidden |
| Tablet Layout | ⭕ | Responsive |
| Mobile Layout | ⭕ | Touch friendly |
| Console Errors | ⭕ | Zero errors |
| Performance | ⭕ | 60fps |

---

## 📊 Results Summary

### **To Complete This Checklist:**

```
Total Tests: 15
Required Passes: 15
Minimum Score: 100%

Green ✅ = Feature Working
Red ❌ = Issue Found
Yellow ⚠️ = Partial Working
```

### **Scoring:**
- **14-15 tests pass:** ✅ EXCELLENT (95%+ quality)
- **12-13 tests pass:** 🟢 GOOD (80%+ quality)
- **10-11 tests pass:** 🟡 ACCEPTABLE (70%+ quality)
- **Below 10:** 🔴 NEEDS WORK (< 70%)

---

## 🎯 Common Issues & Fixes

### **Issue: Sidebar not sliding in**
**Fix:**
```bash
# Check if sidebarOverlay exists in HTML
# Look for id="sidebarOverlay" in dashboardhome.html
# Should have display: none initially
```

### **Issue: Search suggestions not appearing**
**Fix:**
```bash
# Check searchInput element exists
# Verify API endpoint is working
# Check Network tab in DevTools
```

### **Issue: Dropdowns staying open**
**Fix:**
```bash
# Check if click outside handler is attached
# Verify event.stopPropagation() not blocking
# Check z-index values (should be 2000)
```

### **Issue: Mobile menu hamburger not visible**
**Fix:**
```bash
# Check window width is ≤768px
# Check CSS media query @media (max-width: 1024px)
# Verify .toc display: flex in CSS
```

---

## 📞 Support

If you encounter issues:

1. **Check Console:** F12 → Console tab
2. **Check Network:** F12 → Network tab
3. **Check HTML:** F12 → Elements tab
4. **Clear Cache:** Ctrl+Shift+Delete
5. **Hard Reload:** Ctrl+Shift+R
6. **Restart Server:** Stop and restart Django

---

## ✨ Success Criteria

All tests should show:

```
✅ Zero JavaScript errors
✅ All dropdowns opening/closing smoothly
✅ All animations running at 60fps
✅ Mobile menu working on small screens
✅ All links navigating correctly
✅ Search showing suggestions
✅ Posts loading dynamically
✅ No 404 errors
✅ Responsive on all device sizes
```

---

**Last Updated:** December 13, 2025  
**Status:** Ready for Testing  
**Expected Time:** 10-15 minutes to complete all tests

Good luck! 🍀
