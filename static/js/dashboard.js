// Dashboard JavaScript - Dashboard Theme, Modals, Recommendations

// ==================== UTILITY FUNCTIONS ====================
// Add CSS Variables to style tag
if (!document.querySelector('#dynamic-spinner-styles')) {
    const spinnerStyles = document.createElement('style');
    spinnerStyles.id = 'dynamic-spinner-styles';
    spinnerStyles.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .spinner {
            border: 3px solid rgba(31, 156, 238, 0.1);
            border-radius: 50%;
            border-top: 3px solid var(--primary);
            width: 32px;
            height: 32px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
    `;
    document.head.appendChild(spinnerStyles);
}

// ============================================
// Theme Handler
// ============================================
(() => {
    const serverPref = document.querySelector('meta[name="theme-pref"]')?.content || 'system';
    const appearanceUrl = '/accounts/appearance/';
    const setApplied = (applied) => document.documentElement.setAttribute('data-theme', applied);

    let systemMql = null;
    let systemListener = null;

    function systemApplyListener(e){
        const applied = e.matches ? 'dark' : 'light';
        setApplied(applied);
    }

    function scheduleTimeFallback(){
        const now = new Date();
        const hour = now.getHours();
        let next = new Date(now);
        if(hour >=7 && hour < 19){
            next.setHours(19,0,5,0);
        } else {
            if(hour >=19) next.setDate(next.getDate()+1);
            next.setHours(7,0,5,0);
        }
        const delay = Math.max(1000, next.getTime() - now.getTime());
        setTimeout(()=>{
            const h = new Date().getHours();
            setApplied((h>=7 && h<19)?'light':'dark');
            scheduleTimeFallback();
        }, delay + 50);
    }

    async function persistPreference(pref){
        try{ localStorage.setItem('theme_pref', pref); }catch(e){}
        try{
            const csrftoken = (document.cookie.match(/csrftoken=([^;]+)/)||[])[1];
            await fetch(appearanceUrl, {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded','X-CSRFToken':csrftoken,'X-Requested-With':'XMLHttpRequest'}, body: new URLSearchParams({theme:pref})});
        }catch(e){console.warn('Failed to persist theme pref', e)}
    }

    function applyChoice(pref){
        try{ if(systemMql && systemListener) { systemMql.removeEventListener('change', systemListener); systemListener = null; systemMql = null; } }catch(e){}

        if(pref === 'system'){
            if(window.matchMedia){
                systemMql = window.matchMedia('(prefers-color-scheme: dark)');
                const applied = systemMql.matches ? 'dark' : 'light';
                setApplied(applied);
                systemListener = systemApplyListener;
                try{ systemMql.addEventListener('change', systemListener); }catch(e){ try{ systemMql.addListener(systemListener); }catch(e){} }
            } else {
                const hr = new Date().getHours();
                setApplied((hr>=7 && hr<19)?'light':'dark');
                scheduleTimeFallback();
            }
        } else if(pref === 'dark'){
            setApplied('dark');
        } else {
            setApplied('light');
        }
        document.querySelectorAll('.avatar-menu .theme-option').forEach(b=> b.classList.toggle('active', b.getAttribute('data-theme')===pref));
    }

    (function initTheme(){
        let pref = serverPref || null;
        try{ const local = localStorage.getItem('theme_pref'); if(!pref && local) pref = local; }catch(e){}
        if(!pref) pref = 'system';
        applyChoice(pref);
    })();

    window.applyThemeChoice = function(pref, persist=true){ if(persist) persistPreference(pref); applyChoice(pref); };
})();

// ============================================
// Avatar Menu Dropdown (NOT Profile Popup)
// ============================================
const avatarWrapper = document.querySelector('.avatar-wrapper');
const avatarMenu = document.querySelector('.avatar-menu');

if (avatarWrapper && avatarMenu) {
    avatarWrapper.addEventListener('click', e => {
        // Don't open menu if clicking the pfp itself - let profile popup handle it
        if (e.target.classList.contains('pfp') || 
            e.target.classList.contains('pfp-fallback') || 
            e.target.classList.contains('user-profile-trigger')) {
            return;
        }
        e.stopPropagation();
        avatarMenu.style.display = avatarMenu.style.display === 'flex' ? 'none' : 'flex';
    });

    document.addEventListener('click', () => { 
        avatarMenu.style.display = 'none';
    });

    // Theme buttons in menu
    document.querySelectorAll('.avatar-menu .theme-option').forEach(btn=>{
        btn.addEventListener('click', (e)=>{
            e.preventDefault();
            e.stopPropagation();
            const theme = btn.getAttribute('data-theme');
            window.applyThemeChoice(theme, true);
            document.querySelectorAll('.avatar-menu .theme-option').forEach(b=>b.classList.remove('active'));
            btn.classList.add('active');
        });
    });
}

// ============================================
// Notifications Bell & Dropdown
// ============================================
const notificationBell = document.getElementById('notificationBell');
const notificationDropdown = document.getElementById('notificationDropdown');
const notificationList = document.getElementById('notificationList');
const notificationBadge = document.getElementById('notificationBadge');

if (notificationBell && notificationDropdown && notificationList) {
    async function loadNotifications(limit = 6) {
        notificationList.innerHTML = '<div style="padding:12px;color:var(--secondary-text)">Loading...</div>';
        try {
            const res = await fetch(`/accounts/api/notifications/?limit=${limit}`, { credentials: 'include' });
            if (!res.ok) throw new Error('Network error');
            const data = await res.json();
            if (!data || !data.notifications || data.notifications.length === 0) {
                notificationList.innerHTML = '<div style="padding:12px;color:var(--secondary-text)">No notifications.</div>';
                if (notificationBadge) notificationBadge.style.display = 'none';
                return;
            }

            notificationList.innerHTML = '';
            data.notifications.forEach(n => {
                const item = document.createElement('div');
                item.className = 'notification-item';
                item.style.padding = '10px';
                item.style.borderBottom = '1px solid var(--border-color)';
                item.style.cursor = 'pointer';
                // attach metadata for delegated handler (match accounts API shape)
                try { item.dataset.notifId = n.id; } catch(e){}
                try { item.dataset.type = n.type || n.notification_type || ''; } catch(e){}
                if (n.related_user_id) try { item.dataset.relatedUserId = n.related_user_id; } catch(e){}
                if (n.related_user_username) try { item.dataset.relatedUsername = n.related_user_username; } catch(e){}
                if (n.url) try { item.dataset.url = n.url; } catch(e){}
                try { item.dataset.createdAt = n.created_at || n.createdAt || ''; } catch(e){}
                item.innerHTML = `
                    <div class="notif-title" style="font-weight:600;color:var(--text-dark)">${n.title || 'Notification'}</div>
                    <div class="notif-message" style="font-size:0.95rem;color:var(--secondary-text);margin-top:4px">${n.message || ''}</div>
                `;
                notificationList.appendChild(item);
            });

            if (notificationBadge) {
                const unread = data.notifications.filter(x => x.unread).length;
                if (unread > 0) { notificationBadge.style.display = 'flex'; notificationBadge.textContent = unread > 99 ? '99+' : unread; }
                else { notificationBadge.style.display = 'none'; }
            }
        } catch (err) {
            console.error('Failed to load notifications', err);
            notificationList.innerHTML = '<div style="padding:12px;color:var(--danger)">Failed to load.</div>';
        }
    }

    notificationBell.addEventListener('click', async (e) => {
        e.stopPropagation();
        const isOpen = notificationDropdown.style.display === 'block' || notificationDropdown.classList.contains('open');
        if (isOpen) {
            notificationDropdown.style.display = 'none';
            notificationDropdown.classList.remove('open');
            return;
        }
        notificationDropdown.style.display = 'block';
        notificationDropdown.classList.add('open');
        await loadNotifications(6);
    });

    document.addEventListener('click', (e) => {
        if (!notificationDropdown.contains(e.target) && !notificationBell.contains(e.target)) {
            notificationDropdown.style.display = 'none';
            notificationDropdown.classList.remove('open');
        }
    });

    // Delegated click handler for notification items: mark-read and navigate/open modal
    notificationList.addEventListener('click', async function(e){
        const item = e.target.closest('.notification-item');
        if (!item) return;
        e.stopPropagation();
        try { console.debug('Notification clicked', item.dataset); } catch(e){}
        const notifId = item.dataset.notifId;
        const relatedUser = item.dataset.relatedUserId || item.dataset.relateduserid;
        const link = item.dataset.url;
        try{
            if (notifId) {
                await fetch(`/accounts/api/notifications/${notifId}/mark-read/`, {method:'POST', credentials:'include', headers:{'X-CSRFToken': csrfToken(), 'X-Requested-With':'XMLHttpRequest'}});
                // optimistically update badge
                if (notificationBadge) {
                    const cur = parseInt(notificationBadge.textContent||'0');
                    if (!isNaN(cur) && cur>0) notificationBadge.textContent = Math.max(0, cur-1) || '';
                }
            }
        }catch(err){ console.warn('mark-read failed', err); }

        if (relatedUser) {
            window.location.href = `/accounts/chat/${relatedUser}/`;
            return;
        }
        if (link && link !== 'undefined') { window.location.href = link; return; }

        // fallback: open inline modal if available
        if (typeof window.showNotificationModal === 'function') {
            const title = item.querySelector('.notif-title')?.textContent || item.dataset.title || 'Notification';
            const message = item.querySelector('.notif-message')?.textContent || item.dataset.message || '';
            const createdAt = item.dataset.createdAt || new Date().toISOString();
            window.showNotificationModal(notifId, title, message, createdAt, true, item.dataset.type || '', relatedUser || '');
        }
    });
}

// ============================================
// Logout
// ============================================
const logoutBtn = document.getElementById('logout');
if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        document.getElementById('logout-form').submit();
    });
}

// ============================================
// Create Modal
// ============================================
const createBtn = document.querySelector('.create-btn');
const createModal = document.getElementById('createModal');
const blogPostBtn = document.getElementById('blog-post');
const communityPostBtn = document.getElementById('community-post');

if (createBtn && createModal) {
    createBtn.addEventListener('click', () => { 
        createModal.style.display = 'flex'; 
    });

    createModal.addEventListener('click', e => { 
        if (e.target === createModal) {
            createModal.style.display = 'none';
        }
    });
}

if (blogPostBtn) {
    blogPostBtn.addEventListener('click', () => { 
        const url = document.querySelector('[data-create-post-url]')?.dataset.createPostUrl || '/posts/create/';
        window.location.href = url;
    });
}

if (communityPostBtn) {
    communityPostBtn.addEventListener('click', () => { 
        const url = document.querySelector('[data-create-community-url]')?.dataset.createCommunityUrl || '/community/create/';
        window.location.href = url;
    });
}

// ============================================
// Onboarding Interests
// ============================================
const interestsModal = document.getElementById('interestsModal');
const blogTagsModal = document.getElementById('blogTagsModal');
const communityTagsModal = document.getElementById('communityTagsModal');

const interestsGrid = document.getElementById('interestsGrid');
const blogTagsGrid = document.getElementById('blogTagsGrid');
const communityTagsGrid = document.getElementById('communityTagsGrid');

const saveBtn = document.getElementById('saveInterestsBtn');
const saveBlogBtn = document.getElementById('saveBlogTagsBtn');
const saveCommunityBtn = document.getElementById('saveCommunityTagsBtn');

let selectedGameCategories = [];
let selectedBlogTags = [];
let selectedCommunityTags = [];

function getCSRF() {
    return (document.cookie.match(/csrftoken=([^;]+)/)||[])[1] || document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

async function loadTagOptions() {
    try {
        const res = await fetch('/recommend/tag-options/?type=blog');
        const data = await res.json();
        
        blogTagsGrid.innerHTML = '';
        data.tags.forEach(tag => {
            const chip = document.createElement('div');
            chip.className = 'interest-chip';
            chip.textContent = tag.label;
            chip.dataset.category = tag.slug;
            blogTagsGrid.appendChild(chip);
        });

        communityTagsGrid.innerHTML = '';
        data.tags.forEach(tag => {
            const chip = document.createElement('div');
            chip.className = 'interest-chip';
            chip.textContent = tag.label;
            chip.dataset.category = tag.slug;
            communityTagsGrid.appendChild(chip);
        });
    } catch (err) {
        console.error('Failed to load tag options:', err);
    }
}

function makeChipSelectionHandler(gridElement, selectedArray, saveButton, minRequired = 3) {
    gridElement.addEventListener('click', (e) => {
        if (!e.target.classList.contains('interest-chip')) return;
        const chip = e.target;
        const category = chip.dataset.category;
        
        if (chip.classList.contains('selected')) {
            chip.classList.remove('selected');
            selectedArray.splice(selectedArray.indexOf(category), 1);
        } else {
            chip.classList.add('selected');
            selectedArray.push(category);
        }
        
        saveButton.disabled = selectedArray.length < minRequired;
    });
}

if (interestsGrid) makeChipSelectionHandler(interestsGrid, selectedGameCategories, saveBtn, 1);
if (blogTagsGrid) makeChipSelectionHandler(blogTagsGrid, selectedBlogTags, saveBlogBtn, 3);
if (communityTagsGrid) makeChipSelectionHandler(communityTagsGrid, selectedCommunityTags, saveCommunityBtn, 3);

async function checkOnboardingStatus() {
    try {
        const res = await fetch('/recommend/interests/');
        const data = await res.json();
        
        if (!data.completed_game_onboarding) {
            interestsModal?.classList.add('show');
            return;
        }
        
        if (!data.completed_blog_onboarding) {
            await loadTagOptions();
            blogTagsModal?.classList.add('show');
            return;
        }
        
        if (!data.completed_community_onboarding) {
            await loadTagOptions();
            communityTagsModal?.classList.add('show');
            return;
        }
        
        loadAllRecommendations();
    } catch (err) {
        console.error('Failed to check onboarding status:', err);
        loadAllRecommendations();
    }
}

if (saveBtn) {
    saveBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/recommend/interests/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRF()
                },
                body: JSON.stringify({ type: 'game', items: selectedGameCategories })
            });
            const data = await res.json();
            if (data.success) {
                interestsModal?.classList.remove('show');
                await loadTagOptions();
                blogTagsModal?.classList.add('show');
            }
        } catch (err) {
            console.error('Failed to save game interests:', err);
        }
    });
}

if (saveBlogBtn) {
    saveBlogBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/recommend/interests/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRF()
                },
                body: JSON.stringify({ type: 'blog', items: selectedBlogTags })
            });
            const data = await res.json();
            if (data.success) {
                blogTagsModal?.classList.remove('show');
                communityTagsModal?.classList.add('show');
            }
        } catch (err) {
            console.error('Failed to save blog interests:', err);
        }
    });
}

if (saveCommunityBtn) {
    saveCommunityBtn.addEventListener('click', async () => {
        try {
            const res = await fetch('/recommend/interests/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRF()
                },
                body: JSON.stringify({ type: 'community', items: selectedCommunityTags })
            });
            const data = await res.json();
            if (data.success) {
                communityTagsModal?.classList.remove('show');
                loadAllRecommendations();
            }
        } catch (err) {
            console.error('Failed to save community interests:', err);
        }
    });
}

// ============================================
// Recommendations
// ============================================
async function loadAllRecommendations() {
    loadForYouRecommendations();
    loadBlogRecommendations();
    loadCommunityRecommendations();
}

async function loadForYouRecommendations() {
    try {
        const res = await fetch('/recommend/for-you/');
        const data = await res.json();

        const blogContainer = document.getElementById('blogForYouContainer');
        const communityContainer = document.getElementById('communityForYouContainer');
        const gamesForYou = [];

        if (data.results && data.results.length > 0) {
            if (blogContainer) blogContainer.innerHTML = '';
            if (communityContainer) communityContainer.innerHTML = '';

            data.results.forEach(rec => {
                if (rec.type === 'blog') {
                    if (!blogContainer) return;
                    const card = document.createElement('div');
                    card.className = 'unified-post-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => window.location.href = `/posts/${rec.id}/`;
                    const img = rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="width:100%;height:100%;object-fit:cover;object-position:center;"/>` : `<div style="width:100%;height:100%;background:linear-gradient(135deg,#eaeef9,#f7f5f0);"></div>`;
                    const excerpt = rec.excerpt ? `<div class="excerpt">${rec.excerpt}</div>` : '';
                    card.innerHTML = `<div class="post-media">${img}</div><h3>${rec.title}</h3>${excerpt}`;
                    blogContainer.appendChild(card);
                } else if (rec.type === 'community') {
                    if (!communityContainer) return;
                    const card = document.createElement('div');
                    card.className = 'unified-post-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => { window.location.href = `/communities/post/${rec.id}/`; };
                    const img = rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="width:100%;height:100%;object-fit:cover;object-position:center;"/>` : `<div style="width:100%;height:100%;background:linear-gradient(135deg,#f0f4f8,#f7f5f0);"></div>`;
                    const excerpt = rec.excerpt ? `<div class="excerpt">${rec.excerpt}</div>` : '';
                    card.innerHTML = `<div class="post-media">${img}</div><h3>${rec.title}</h3>${excerpt}`;
                    communityContainer.appendChild(card);
                } else if (rec.type === 'game') {
                    gamesForYou.push(rec);
                }
            });

            try { sessionStorage.setItem('forYouGames', JSON.stringify(gamesForYou)); } catch (e) { }

            if ((blogContainer && blogContainer.children.length > 0) || (communityContainer && communityContainer.children.length > 0)) {
                document.getElementById('forYouSection')?.style.display = 'block';
            } else {
                document.getElementById('forYouSection')?.style.display = 'none';
            }

            const homeToggle = document.getElementById('homeForYouToggle');
            if (homeToggle && ((blogContainer && blogContainer.children.length>0) || (communityContainer && communityContainer.children.length>0))) {
                document.querySelectorAll('.filter-bubble').forEach(b => b.classList.remove('active'));
                homeToggle.classList.add('active');
            }
        }
    } catch (err) {
        console.error('Failed to load recommendations:', err);
    }
}

async function loadBlogRecommendations() {
    try {
        const res = await fetch('/recommend/blog-recommendations/');
        const data = await res.json();
        if (data.results && data.results.length > 0) {
            const container = document.getElementById('blogForYouContainer');
            if (container) {
                container.innerHTML = '';
                data.results.forEach(rec => {
                    const card = document.createElement('div');
                    card.className = 'unified-post-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => window.location.href = `/posts/${rec.id}/`;
                    const img = rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="width:100%;height:100%;object-fit:cover;object-position:center;"/>` : `<div style="width:100%;height:100%;background:linear-gradient(135deg,#eaeef9,#f7f5f0);"></div>`;
                    const excerpt = rec.excerpt ? `<div class="excerpt">${rec.excerpt}</div>` : '';
                    card.innerHTML = `<div class="post-media">${img}</div><h3>${rec.title}</h3>${excerpt}`;
                    container.appendChild(card);
                });
            }
        }
    } catch (err) {
        console.error('Failed to load blog recommendations:', err);
    }
}

async function loadCommunityRecommendations() {
    try {
        const res = await fetch('/recommend/community-recommendations/');
        const data = await res.json();
        console.log('Community recommendations data:', data);
        if (data.results && data.results.length > 0) {
            const container = document.getElementById('communityForYouContainer');
            if (!container) return;
            container.innerHTML = '';

            data.results.forEach(rec => {
                const card = document.createElement('div');
                card.className = 'unified-post-card';
                card.style.background = 'var(--card-bg)';
                card.style.border = '1px solid var(--border-color)';
                card.style.borderRadius = '12px';
                card.style.overflow = 'hidden';
                card.style.cursor = 'pointer';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.transition = 'transform 0.2s, box-shadow 0.2s';
                card.style.width = 'min(100%, 600px)';
                card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)';

                // Image area with avatars
                const imgWrapper = document.createElement('div');
                imgWrapper.style.position = 'relative';
                imgWrapper.style.width = '100%';
                imgWrapper.style.aspectRatio = '16/9';
                imgWrapper.style.backgroundColor = '#cbd5e1';
                imgWrapper.style.display = 'flex';
                imgWrapper.style.alignItems = 'center';
                imgWrapper.style.justifyContent = 'center';
                imgWrapper.style.overflow = 'hidden';

                if (rec.image) {
                    const img = document.createElement('img');
                    img.src = rec.image;
                    img.alt = rec.title || '';
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'cover';
                    img.style.objectPosition = 'center';
                    imgWrapper.appendChild(img);
                    img.onerror = () => {
                        img.style.display = 'none';
                        const fallback = document.createElement('div');
                        fallback.style.width = '100%';
                        fallback.style.height = '100%';
                        fallback.style.background = 'linear-gradient(135deg, #cbd5e1, #94a3b8)';
                        fallback.style.display = 'flex';
                        fallback.style.alignItems = 'center';
                        fallback.style.justifyContent = 'center';
                        fallback.textContent = 'Image not found';
                        fallback.style.color = '#64748b';
                        fallback.style.fontSize = '14px';
                        imgWrapper.appendChild(fallback);
                    };
                } else {
                    const fallback = document.createElement('div');
                    fallback.style.width = '100%';
                    fallback.style.height = '100%';
                    fallback.style.background = 'linear-gradient(135deg, #cbd5e1, #94a3b8)';
                    fallback.style.display = 'flex';
                    fallback.style.alignItems = 'center';
                    fallback.style.justifyContent = 'center';
                    fallback.textContent = 'No image';
                    fallback.style.color = '#64748b';
                    fallback.style.fontSize = '14px';
                    imgWrapper.appendChild(fallback);
                }

                // Community avatar (top-left)
                const commAvatar = document.createElement('div');
                commAvatar.style.position = 'absolute';
                commAvatar.style.left = '12px';
                commAvatar.style.top = '12px';
                commAvatar.style.width = '48px';
                commAvatar.style.height = '48px';
                commAvatar.style.borderRadius = '50%';
                commAvatar.style.border = '3px solid #fff';
                commAvatar.style.display = 'flex';
                commAvatar.style.alignItems = 'center';
                commAvatar.style.justifyContent = 'center';
                commAvatar.style.background = '#e5e7eb';
                commAvatar.style.overflow = 'hidden';
                commAvatar.style.cursor = 'pointer';
                commAvatar.style.zIndex = '2';
                if (rec.community_image) {
                    const ca = document.createElement('img');
                    ca.src = rec.community_image;
                    ca.style.width = '100%';
                    ca.style.height = '100%';
                    ca.style.objectFit = 'cover';
                    commAvatar.appendChild(ca);
                } else {
                    commAvatar.textContent = rec.community_name ? rec.community_name.slice(0,1).toUpperCase() : 'C';
                    commAvatar.style.fontWeight = '700';
                    commAvatar.style.color = '#374151';
                    commAvatar.style.fontSize = '20px';
                }
                commAvatar.onclick = (e) => { e.stopPropagation(); if (rec.community_id) window.location.href = `/communities/${rec.community_id}/`; };
                imgWrapper.appendChild(commAvatar);

                // Author avatar (top-right)
                const authAvatar = document.createElement('div');
                authAvatar.style.position = 'absolute';
                authAvatar.style.right = '12px';
                authAvatar.style.top = '12px';
                authAvatar.style.width = '48px';
                authAvatar.style.height = '48px';
                authAvatar.style.borderRadius = '50%';
                authAvatar.style.border = '3px solid #fff';
                authAvatar.style.display = 'flex';
                authAvatar.style.alignItems = 'center';
                authAvatar.style.justifyContent = 'center';
                authAvatar.style.background = '#d1d5db';
                authAvatar.style.overflow = 'hidden';
                authAvatar.style.cursor = 'pointer';
                authAvatar.style.zIndex = '2';
                if (rec.author_avatar) {
                    const aa = document.createElement('img');
                    aa.src = rec.author_avatar;
                    aa.style.width = '100%';
                    aa.style.height = '100%';
                    aa.style.objectFit = 'cover';
                    authAvatar.appendChild(aa);
                } else {
                    authAvatar.textContent = rec.author_username ? rec.author_username.slice(0,1).toUpperCase() : 'U';
                    authAvatar.style.fontWeight = '700';
                    authAvatar.style.color = '#374151';
                    authAvatar.style.fontSize = '20px';
                }
                authAvatar.onclick = (e) => { e.stopPropagation(); if (rec.author_id) window.location.href = `/accounts/profile/${rec.author_id}/`; };
                imgWrapper.appendChild(authAvatar);

                card.appendChild(imgWrapper);

                // Content section
                const content = document.createElement('div');
                content.style.padding = '16px';
                content.style.display = 'flex';
                content.style.flexDirection = 'column';
                content.style.gap = '12px';

                // Community and author info
                const meta = document.createElement('div');
                meta.style.display = 'flex';
                meta.style.gap = '8px';
                meta.style.alignItems = 'center';
                meta.style.fontSize = '0.85rem';
                meta.style.color = 'var(--secondary-text)';
                meta.innerHTML = `<strong style="color:var(--text-dark);">${rec.community_name || 'Community'}</strong> • <span>${rec.author_username || 'User'}</span>`;
                content.appendChild(meta);

                // Title
                const title = document.createElement('h3');
                title.style.margin = '0';
                title.style.fontSize = '1.1rem';
                title.style.fontWeight = '700';
                title.style.color = 'var(--text-dark)';
                title.style.lineHeight = '1.4';
                title.textContent = rec.title || '';
                content.appendChild(title);

                // Excerpt
                if (rec.excerpt) {
                    const excerpt = document.createElement('p');
                    excerpt.style.margin = '0';
                    excerpt.style.color = 'var(--secondary-text)';
                    excerpt.style.fontSize = '0.95rem';
                    excerpt.style.lineHeight = '1.5';
                    excerpt.style.display = '-webkit-box';
                    excerpt.style.webkitLineClamp = '2';
                    excerpt.style.webkitBoxOrient = 'vertical';
                    excerpt.style.overflow = 'hidden';
                    excerpt.textContent = rec.excerpt;
                    content.appendChild(excerpt);
                }

                // Action buttons
                const actions = document.createElement('div');
                actions.style.display = 'flex';
                actions.style.gap = '12px';
                actions.style.alignItems = 'center';
                actions.style.marginTop = '8px';
                actions.style.paddingTop = '12px';
                actions.style.borderTop = '1px solid var(--border-color)';
                actions.style.flexWrap = 'wrap';

                // Dislike button (create first so like button can reference it)
                const dislikeBtn = document.createElement('button');
                dislikeBtn.className = 'foryou-action-btn';
                dislikeBtn.style.cssText = 'background:none;border:none;cursor:pointer;padding:2px;display:flex;align-items:center;gap:4px;color:var(--secondary-text);font-size:0.85rem;transition:color 0.2s;min-width:auto;';
                dislikeBtn.innerHTML = `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M17 14V2'/><path d='M9 18.12 10 14H4.17a2 2 0 0 1-1.92-2.56l2.33-8A2 2 0 0 1 6.5 2H20a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2h-2.76a2 2 0 0 0-1.79 1.11L12 22a3.13 3.13 0 0 1-3-3.88Z'/></svg><span class='dislike-count'>${rec.dislikes_count||0}</span>`;

                // Like button
                const likeBtn = document.createElement('button');
                likeBtn.className = 'foryou-action-btn';
                likeBtn.style.cssText = 'background:none;border:none;cursor:pointer;padding:4px 6px;display:flex;align-items:center;gap:4px;color:var(--secondary-text);font-size:0.8rem;transition:color 0.2s;min-width:auto;border-radius:4px;';
                likeBtn.innerHTML = `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M7 10v12'/><path d='M15 5.88 14 10h5.83a2 2 0 0 1 1.92 2.56l-2.33 8A2 2 0 0 1 17.5 22H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h2.76a2 2 0 0 0 1.79-1.11L12 2a3.13 3.13 0 0 1 3 3.88Z'/></svg><span class='like-count'>${rec.likes_count||0}</span>`;
                
                likeBtn.addEventListener('click', async (e) => { e.stopPropagation(); 
                    try { 
                        const r = await fetch(`/communities/api/post/${rec.id}/like/`, { method:'POST',credentials:'include',headers:{'X-CSRFToken':csrfToken(),'X-Requested-With':'XMLHttpRequest'} }); 
                        if(!r.ok) throw new Error('Network'); 
                        const j = await r.json(); 
                        likeBtn.querySelector('.like-count').textContent = j.likes_count || 0; 
                        dislikeBtn.querySelector('.dislike-count').textContent = j.dislikes_count || 0;
                        if(j.liked) { likeBtn.style.color='var(--primary)'; dislikeBtn.style.color='var(--secondary-text)'; } 
                        else { likeBtn.style.color='var(--secondary-text)'; } 
                    } catch(err){console.error(err);} 
                });
                actions.appendChild(likeBtn);
                
                dislikeBtn.addEventListener('click', async (e) => { e.stopPropagation(); 
                    try { 
                        const r = await fetch(`/communities/api/post/${rec.id}/dislike/`, { method:'POST',credentials:'include',headers:{'X-CSRFToken':csrfToken(),'X-Requested-With':'XMLHttpRequest'} }); 
                        if(!r.ok) throw new Error('Network'); 
                        const j = await r.json(); 
                        dislikeBtn.querySelector('.dislike-count').textContent = j.dislikes_count || 0; 
                        likeBtn.querySelector('.like-count').textContent = j.likes_count || 0;
                        if(j.disliked) { dislikeBtn.style.color='#e74c3c'; likeBtn.style.color='var(--secondary-text)'; } 
                        else { dislikeBtn.style.color='var(--secondary-text)'; } 
                    } catch(err){console.error(err);} 
                });
                actions.appendChild(dislikeBtn);

                // Comment button
                const commentBtn = document.createElement('a');
                commentBtn.href = `/communities/post/${rec.id}/`;
                commentBtn.style.cssText = 'display:flex;align-items:center;gap:4px;color:var(--secondary-text);text-decoration:none;font-size:0.85rem;transition:color 0.2s;padding:2px;';
                commentBtn.innerHTML = `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2'><path d='M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z'/></svg><span>${rec.comments_count||0}</span>`;
                commentBtn.onmouseover = () => commentBtn.style.color = 'var(--primary)';
                commentBtn.onmouseout = () => commentBtn.style.color = 'var(--secondary-text)';
                actions.appendChild(commentBtn);

                // Bookmark button
                const bookmarkBtn = document.createElement('button');
                bookmarkBtn.className = 'foryou-action-btn';
                bookmarkBtn.style.cssText = 'background:none;border:none;cursor:pointer;padding:2px;display:flex;align-items:center;gap:4px;color:var(--secondary-text);font-size:0.85rem;transition:color 0.2s;margin-left:auto;';
                bookmarkBtn.innerHTML = rec.user_bookmarked ? `<svg width='16' height='16' fill='currentColor' viewBox='0 0 24 24'><path d='m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z'/></svg>` : `<svg width='16' height='16' fill='none' stroke='currentColor' stroke-width='2' viewBox='0 0 24 24'><path d='m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z'/></svg>`;
                if (rec.user_bookmarked) bookmarkBtn.style.color = 'var(--primary)';
                
                bookmarkBtn.addEventListener('click', async (e) => { e.stopPropagation(); 
                    try { 
                        const r = await fetch(`/communities/api/post/${rec.id}/bookmark/`, { method:'POST',credentials:'include',headers:{'X-CSRFToken':csrfToken(),'X-Requested-With':'XMLHttpRequest'} }); 
                        if(!r.ok) throw new Error('Network'); 
                        const j = await r.json(); 
                        bookmarkBtn.style.color = j.bookmarked ? 'var(--primary)' : 'var(--secondary-text)'; 
                        bookmarkBtn.innerHTML = j.bookmarked ? `<svg width='16' height='16' fill='currentColor' viewBox='0 0 24 24'><path d='m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2Z'/></svg>` : `<svg width='16' height='16' fill='none' stroke='currentColor' stroke-width='2' viewBox='0 0 24 24'><path d='m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z'/></svg>`; 
                    } catch(err){console.error(err);} 
                });
                actions.appendChild(bookmarkBtn);

                // Menu button (ellipsis) with dropdown for Report and Share
                const menuWrapper = document.createElement('div');
                menuWrapper.style.position = 'relative';
                menuWrapper.style.display = 'inline-block';
                menuWrapper.style.zIndex = '10';
                
                const menuBtn = document.createElement('button');
                menuBtn.className = 'foryou-action-btn';
                menuBtn.style.cssText = 'background:none;border:none;cursor:pointer;padding:2px;display:flex;align-items:center;gap:4px;color:var(--secondary-text);font-size:0.85rem;transition:color 0.2s;';
                menuBtn.innerHTML = `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='currentColor'><circle cx='5' cy='12' r='2'/><circle cx='12' cy='12' r='2'/><circle cx='19' cy='12' r='2'/></svg>`;
                
                // Dropdown menu
                const dropdown = document.createElement('div');
                dropdown.style.cssText = 'position:absolute;top:calc(100% + 4px);right:0;background:var(--card-bg);border:1px solid var(--border-color);border-radius:8px;min-width:140px;z-index:10000;display:none;box-shadow:0 12px 24px rgba(0,0,0,0.15);overflow:hidden;';
                
                // Share option
                const shareOption = document.createElement('button');
                shareOption.style.cssText = 'display:block;width:100%;padding:10px 12px;border:none;background:none;text-align:left;cursor:pointer;color:var(--text-dark);font-size:0.9rem;transition:background 0.2s;';
                shareOption.textContent = 'Share';
                shareOption.onmouseover = () => shareOption.style.background = 'var(--hover-bg, rgba(0,0,0,0.05))';
                shareOption.onmouseout = () => shareOption.style.background = 'none';
                shareOption.onclick = (e) => { e.stopPropagation(); 
                    const url = window.location.origin + `/communities/post/${rec.id}/`;
                    if(navigator.share) {
                        navigator.share({title: rec.title, text: rec.excerpt, url: url});
                    } else {
                        alert('Share URL: ' + url);
                    }
                    dropdown.style.display = 'none';
                };
                dropdown.appendChild(shareOption);
                
                // Report option
                const reportOption = document.createElement('button');
                reportOption.style.cssText = 'display:block;width:100%;padding:10px 12px;border:none;background:none;text-align:left;cursor:pointer;color:#e11d48;font-size:0.9rem;transition:background 0.2s;border-top:1px solid var(--border-color);';
                reportOption.textContent = 'Report';
                reportOption.onmouseover = () => reportOption.style.background = 'var(--hover-bg, rgba(0,0,0,0.05))';
                reportOption.onmouseout = () => reportOption.style.background = 'none';
                reportOption.onclick = (e) => { e.stopPropagation(); 
                    const reason = prompt('Why are you reporting this post?'); 
                    if(!reason) return; 
                    try { 
                        fetch(`/communities/api/post/${rec.id}/report/`, { method:'POST',credentials:'include',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken()},body:JSON.stringify({reason}) }).then(r => { if(r.ok) alert('Report submitted'); else alert('Failed'); }); 
                    } catch(err){console.error(err);} 
                    dropdown.style.display = 'none';
                };
                dropdown.appendChild(reportOption);
                
                menuBtn.onclick = (e) => { e.stopPropagation(); dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none'; };
                
                // Close dropdown on outside click
                document.addEventListener('click', (e) => {
                    if (!menuWrapper.contains(e.target)) {
                        dropdown.style.display = 'none';
                    }
                });
                
                menuWrapper.appendChild(menuBtn);
                menuWrapper.appendChild(dropdown);
                actions.appendChild(menuWrapper);

                content.appendChild(actions);
                card.appendChild(content);

                // Navigate to post detail on card click (excluding buttons/links)
                card.addEventListener('click', (e) => { 
                    if (e.target.closest('button') || e.target.closest('a')) return; 
                    window.location.href = `/communities/post/${rec.id}/`; 
                });

                // Hover effect
                card.onmouseover = () => { card.style.transform = 'translateY(-4px)'; card.style.boxShadow = '0 12px 30px rgba(0,0,0,0.12)'; };
                card.onmouseout = () => { card.style.transform = 'translateY(0)'; card.style.boxShadow = '0 4px 12px rgba(0,0,0,0.08)'; };

                container.appendChild(card);
            });
        }
    } catch (err) {
        console.error('Failed to load community recommendations:', err);
    }
}

document.getElementById('refreshRecommendations')?.addEventListener('click', loadForYouRecommendations);

const homeForYouToggle = document.getElementById('homeForYouToggle');
if (homeForYouToggle) {
    homeForYouToggle.addEventListener('click', async (e) => {
        e.preventDefault();
        const isActive = homeForYouToggle.classList.contains('active');
        const forYouSectionEl = document.getElementById('forYouSection');
        if (isActive) {
            homeForYouToggle.classList.remove('active');
            document.querySelectorAll('.filter-bubble').forEach(b => b.classList.remove('active'));
            document.querySelector('.filter-bubble[data-sort="latest"]')?.classList.add('active');
            if (forYouSectionEl) forYouSectionEl.style.display = 'none';
            return;
        }
        document.querySelectorAll('.filter-bubble').forEach(b => b.classList.remove('active'));
        homeForYouToggle.classList.add('active');
        if (forYouSectionEl) forYouSectionEl.style.display = 'block';
        await loadForYouRecommendations();
        const y = (forYouSectionEl) ? Math.max(forYouSectionEl.getBoundingClientRect().top + window.scrollY - 100, 0) : 0;
        window.scrollTo({ top: y, behavior: 'smooth' });
    });
}

// Check onboarding on page load
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(checkOnboardingStatus, 500);
});

// ============================================
// Search Bar
// ============================================
const searchBar = document.getElementById('mobileSearch');
if (searchBar) {
    const searchInput = searchBar.querySelector('input');
    const searchIcon = searchBar.querySelector('svg');
    const navActions = document.querySelector('.nav-actions');

    const toggleSearch = (e) => {
        e.stopPropagation();
        searchBar.classList.toggle('expanded');
        searchBar.classList.toggle('collapsed');

        if (searchBar.classList.contains('expanded') && window.innerWidth <= 768) {
            searchInput.focus();
            navActions.classList.add('hide-on-search');
        } else {
            navActions.classList.remove('hide-on-search');
            searchInput.focus();
        }
    };

    searchIcon.addEventListener('click', toggleSearch);
    searchBar.addEventListener('click', (e)=>{ if(e.target===searchBar) toggleSearch(e); });

    document.addEventListener('click', (e) => {
        if (!searchBar.contains(e.target)) {
            searchBar.classList.remove('expanded');
            searchBar.classList.add('collapsed');
            navActions.classList.remove('hide-on-search');
        }
    });
}

// ============================================
// Sidebar Mobile
// ============================================
const tocBtn = document.getElementById('mobileTOC');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

if (sidebar && window.innerWidth <= 768) {
    sidebar.classList.add('mobile');
}

if (tocBtn) {
    tocBtn.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        }
    });
}

if (sidebarOverlay) {
    sidebarOverlay.addEventListener('click', () => {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    });
}

window.addEventListener('resize', () => {
    if (window.innerWidth > 768) {
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
    } else {
        sidebar.classList.add('mobile');
    }
});

// ============================================
// CREATE BUTTON MODAL HANDLER
// ============================================
document.querySelector('.create-btn')?.addEventListener('click', function() {
    const modal = document.getElementById('createModal');
    if (modal) {
        modal.style.display = 'flex';
    }
});

document.getElementById('createModal')?.addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
    }
});

document.getElementById('community-post')?.addEventListener('click', function() {
    window.location.href = '/communities/create-post/';
});

document.getElementById('blog-post')?.addEventListener('click', function() {
    window.location.href = '/posts/create/';
});

// ============================================
// NOTIFICATION BELL DROPDOWN
// ============================================
document.getElementById('notificationBell')?.addEventListener('click', function(e) {
    e.stopPropagation();
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        document.querySelectorAll('.dropdown-menu').forEach(d => d.style.display = 'none');
        dropdown.style.display = isVisible ? 'none' : 'block';
    }
});

// ============================================
// USER AVATAR MENU DROPDOWN (for new dropdown)
// ============================================
document.querySelectorAll('.user-profile-trigger')?.forEach(trigger => {
    trigger.addEventListener('click', function(e) {
        if (e.target.closest('.dropdown-menu') || e.target.closest('ul')) return;
        e.stopPropagation();
        const dropdown = document.getElementById('userMenuDropdown');
        if (dropdown) {
            const isVisible = dropdown.style.display === 'block';
            document.querySelectorAll('.dropdown-menu').forEach(d => d.style.display = 'none');
            dropdown.style.display = isVisible ? 'none' : 'block';
        }
    });
});

// LOGOUT HANDLER
document.getElementById('logout')?.addEventListener('click', function(e) {
    e.preventDefault();
    const form = document.getElementById('logout-form');
    if (form) {
        form.submit();
    }
});

// ============================================
// GLOBAL DROPDOWN CLOSE HANDLER
// ============================================
document.addEventListener('click', function(e) {
    const isNotificationBtn = e.target.closest('.notification-btn');
    const isNotificationDropdown = e.target.closest('#notificationDropdown');
    const isAvatarWrapper = e.target.closest('.avatar-wrapper');
    const isUserMenuDropdown = e.target.closest('#userMenuDropdown');

    if (!isNotificationBtn && !isNotificationDropdown) {
        const notifDropdown = document.getElementById('notificationDropdown');
        if (notifDropdown) notifDropdown.style.display = 'none';
    }

    if (!isAvatarWrapper && !isUserMenuDropdown) {
        const userDropdown = document.getElementById('userMenuDropdown');
        if (userDropdown) userDropdown.style.display = 'none';
    }
});

// ============================================
// FILTER BUBBLES & COMMUNITY POSTS
// ============================================
document.querySelectorAll('.filter-bubble').forEach(btn => {
    btn.addEventListener('click', async function() {
        document.querySelectorAll('.filter-bubble').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const sortType = this.dataset.sort;
        await loadCommunityPosts(sortType);
    });
});

async function loadCommunityPosts(sort = 'for_you') {
    const feedContainer = document.getElementById('community-feed');
    if (!feedContainer) return;
    
    feedContainer.style.display = 'flex';
    
    // Show professional loading state
    feedContainer.innerHTML = `
        <div style="text-align:center;padding:60px 20px;">
            <div class="spinner" style="margin-bottom:16px;"></div>
            <p style="margin:0;color:var(--secondary-text);font-size:14px;">Loading posts...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/dashboard/community-posts-api/?sort=${sort}`);
        if (!response.ok) throw new Error('Failed to load posts');
        
        const data = await response.json();
        
        if (data.posts && data.posts.length > 0) {
            feedContainer.innerHTML = '';
            data.posts.forEach(post => {
                feedContainer.appendChild(createPostCard(post));
            });
        } else {
            feedContainer.innerHTML = `
                <div style="text-align:center;padding:60px 20px;max-width:400px;margin:0 auto;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:0.3;margin-bottom:20px;">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <path d="M9 9h.01M15 9h.01M9 15h6"/>
                    </svg>
                    <h3 style="margin:0 0 8px;font-size:18px;color:var(--text-dark);font-weight:600;">No posts yet</h3>
                    <p style="margin:0;color:var(--secondary-text);font-size:14px;line-height:1.6;">
                        ${sort === 'for_you' ? 'Posts from your interests will appear here. Try following some communities!' : 'No posts match this filter. Try another one!'}
                    </p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading posts:', error);
    }
}

function createPostCard(post) {
    const card = document.createElement('div');
    card.className = 'post-card';
    card.style.cssText = 'background:var(--card-bg);border-radius:12px;padding:16px;box-shadow:var(--card-shadow);border:1px solid var(--border);';
    
    const authorAvatar = post.author_avatar || '/static/default-avatar.png';
    const authorUrl = post.author_profile_url || `/accounts/profile/${post.author_username}/`;
    
    card.innerHTML = `
        <div style="display:flex;gap:12px;margin-bottom:12px;align-items:center;">
            <img src="${authorAvatar}" alt="${post.author_username}"
                 style="width:40px;height:40px;border-radius:50%;object-fit:cover;cursor:pointer;"
                 onclick="window.location.href='${authorUrl}'">
            <div style="flex:1;">
                <div style="font-weight:600;color:var(--text-dark);"><a href="${authorUrl}" style="color:var(--text-dark);text-decoration:none;cursor:pointer;">${post.author_username}</a></div>
                <div style="font-size:0.85rem;color:var(--secondary-text);">${post.created_at || 'Just now'}</div>
            </div>
        </div>
        <h3 style="margin:0 0 8px;font-size:1.1rem;color:var(--text-dark);">${post.title || 'Untitled'}</h3>
        <p style="color:var(--secondary-text);margin:0 0 12px;line-height:1.4;">${post.content_preview || post.content || ''}</p>
        <div style="display:flex;gap:16px;align-items:center;">
            <button class="like-btn" data-post-id="${post.id}" style="background:none;border:none;color:var(--secondary-text);cursor:pointer;display:flex;align-items:center;gap:6px;font-size:0.9rem;transition:color 0.2s;" onmouseover="this.style.color='var(--primary)'" onmouseout="this.style.color='var(--secondary-text)'">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3.172 12.519a1 1 0 0 1 1.414-1.414L12 19.172l7.414-7.414a1 1 0 1 1 1.414 1.414l-8.121 8.121a1 1 0 0 1-1.414 0l-8.121-8.121z"/><path d="M12 2v8m0 0l-7-7m7 7l7-7"/></svg>
                <span>${post.likes_count || 0}</span>
            </button>
            <a href="${post.url || '#'}" style="color:var(--primary);text-decoration:none;font-weight:500;font-size:0.9rem;transition:opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">View post →</a>
        </div>
    `;
    
    return card;
}

// Auto-load "For you" feed on page load
document.addEventListener('DOMContentLoaded', function() {
    const forYouBtn = document.querySelector('.filter-bubble[data-sort="for_you"]');
    if (forYouBtn && document.getElementById('community-feed')) {
        loadCommunityPosts('for_you');
    }
});

// ============================================
// SEARCH FUNCTIONALITY
// ============================================
const searchInput = document.getElementById('searchInput');
let searchTimeout;
let suggestionsDropdown;

if (searchInput) {
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            hideSuggestions();
            return;
        }
        
        searchTimeout = setTimeout(async () => {
            try {
                const response = await fetch(`/dashboard/search-suggestions/?q=${encodeURIComponent(query)}`);
                const data = await response.json();
                showSearchSuggestions(data.suggestions || []);
            } catch (error) {
                console.error('Search suggestions error:', error);
            }
        }, 300);
    });
}

function showSearchSuggestions(suggestions) {
    if (!suggestionsDropdown) {
        suggestionsDropdown = document.createElement('div');
        suggestionsDropdown.id = 'searchSuggestions';
        suggestionsDropdown.className = 'dropdown-menu';
        suggestionsDropdown.style.cssText = 'position:absolute;top:100%;left:0;right:0;background:var(--card-bg);border:1px solid var(--border);border-radius:8px;margin-top:4px;max-height:300px;overflow-y:auto;z-index:2000;box-shadow:0 8px 24px rgba(0,0,0,0.15);';
        
        const searchBar = searchInput?.parentElement;
        if (searchBar) {
            searchBar.style.position = 'relative';
            searchBar.appendChild(suggestionsDropdown);
        }
    }
    
    if (suggestions.length === 0) {
        suggestionsDropdown.innerHTML = '<div style="padding:12px;text-align:center;color:var(--secondary-text);">No results found</div>';
    } else {
        suggestionsDropdown.innerHTML = suggestions.map(s => `
            <a href="${s.url || '#'}" style="display:block;padding:12px 16px;border-bottom:1px solid var(--border);color:var(--text-dark);text-decoration:none;transition:background 0.2s;cursor:pointer;" onmouseover="this.style.background='var(--bg)'" onmouseout="this.style.background='transparent'">
                <div style="font-weight:600;font-size:0.95rem;">${s.title || s.name || 'Untitled'}</div>
                <div style="font-size:0.8rem;color:var(--secondary-text);">${s.type || s.category || 'Content'}</div>
            </a>
        `).join('');
    }
    
    suggestionsDropdown.style.display = 'block';
}

function hideSuggestions() {
    if (suggestionsDropdown) {
        suggestionsDropdown.style.display = 'none';
    }
}

document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-bar')) {
        hideSuggestions();
    }
});

// ============================================
// CSS ANIMATION FOR SPINNER
// ============================================
if (!document.getElementById('spinnerCss')) {
    const style = document.createElement('style');
    style.id = 'spinnerCss';
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
}
// ==================== AUTO-LOAD ON PAGE LOAD ====================
document.addEventListener('DOMContentLoaded', function() {
    // Auto-load "For You" feed
    const forYouBtn = document.querySelector('.filter-bubble[data-sort="for_you"]');
    if (forYouBtn && document.getElementById('community-feed')) {
        loadCommunityPosts('for_you');
    }
    
    // Load notifications
    if (document.getElementById('notificationBell')) {
        loadNotifications(6);
    }
    
    // Initialize onboarding if needed
    setTimeout(checkOnboardingStatus, 500);
});
