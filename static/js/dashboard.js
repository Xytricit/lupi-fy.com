// Dashboard JavaScript - Dashboard Theme, Modals, Recommendations

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
            const res = await fetch(`/notifications/api/recent/?limit=${limit}`);
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
                item.innerHTML = `
                    <div style="font-weight:600;color:var(--text-dark)">${n.title || 'Notification'}</div>
                    <div style="font-size:0.95rem;color:var(--secondary-text);margin-top:4px">${n.message || ''}</div>
                `;
                item.addEventListener('click', () => {
                    window.location.href = n.url || '{% url "notifications_page" %}';
                });
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
                    card.className = 'for-you-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => window.location.href = `/posts/${rec.id}/`;
                    card.innerHTML = `
                        <div style="width:100%;height:140px;display:flex;align-items:center;justify-content:center;background:var(--muted-bg, #f3f4f6);border-radius:8px;overflow:hidden;">
                            ${rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="max-width:100%;max-height:100%;object-fit:contain;"/>` : `<div style=\"width:60%;height:60%;background:linear-gradient(135deg,#eaeef9,#f7f5f0);border-radius:6px;\"></div>`}
                        </div>
                        <div style="margin-top:8px;font-weight:700;color:var(--text-dark);">${rec.title}</div>
                        ${rec.excerpt ? `<div style="color:var(--secondary-text);font-size:0.95rem;margin-top:6px;">${rec.excerpt}</div>` : ''}
                    `;
                    blogContainer.appendChild(card);
                } else if (rec.type === 'community') {
                    if (!communityContainer) return;
                    const card = document.createElement('div');
                    card.className = 'for-you-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => { window.location.href = `/communities/post/${rec.id}/`; };
                    card.innerHTML = `
                        <div style="width:100%;height:140px;display:flex;align-items:center;justify-content:center;background:var(--muted-bg, #f3f4f6);border-radius:8px;overflow:hidden;">
                            ${rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="max-width:100%;max-height:100%;object-fit:contain;"/>` : `<div style=\"width:60%;height:60%;background:linear-gradient(135deg,#f0f4f8,#f7f5f0);border-radius:6px;\"></div>`}
                        </div>
                        <div style="margin-top:8px;font-weight:700;color:var(--text-dark);">${rec.title}</div>
                        ${rec.excerpt ? `<div style="color:var(--secondary-text);font-size:0.95rem;margin-top:6px;">${rec.excerpt}</div>` : ''}
                    `;
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
                    card.className = 'for-you-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => window.location.href = `/posts/${rec.id}/`;
                    card.innerHTML = `
                        <div style="width:100%;height:140px;display:flex;align-items:center;justify-content:center;background:#f3f4f6;border-radius:8px;overflow:hidden;">
                            ${rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="max-width:100%;max-height:100%;object-fit:contain;"/>` : `<div style=\"width:60%;height:60%;background:linear-gradient(135deg,#eaeef9,#f7f5f0);border-radius:6px;\"></div>`}
                        </div>
                        <div style="margin-top:8px;font-weight:700;color:var(--text-dark);">${rec.title}</div>
                        ${rec.excerpt ? `<div style="color:var(--secondary-text);font-size:0.95rem;margin-top:6px;">${rec.excerpt}</div>` : ''}
                    `;
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
        if (data.results && data.results.length > 0) {
            const container = document.getElementById('communityForYouContainer');
            if (container) {
                container.innerHTML = '';
                data.results.forEach(rec => {
                    const card = document.createElement('div');
                    card.className = 'for-you-card';
                    card.style.cursor = 'pointer';
                    card.onclick = () => { window.location.href = `/communities/post/${rec.id}/`; };
                    card.innerHTML = `
                        <div style="width:100%;height:140px;display:flex;align-items:center;justify-content:center;background:#f3f4f6;border-radius:8px;overflow:hidden;">
                            ${rec.image ? `<img src="${rec.image}" alt="${rec.title}" style="max-width:100%;max-height:100%;object-fit:contain;"/>` : `<div style=\"width:60%;height:60%;background:linear-gradient(135deg,#f0f4f8,#f7f5f0);border-radius:6px;\"></div>`}
                        </div>
                        <div style="margin-top:8px;font-weight:700;color:var(--text-dark);">${rec.title}</div>
                        ${rec.excerpt ? `<div style="color:var(--secondary-text);font-size:0.95rem;margin-top:6px;">${rec.excerpt}</div>` : ''}
                    `;
                    container.appendChild(card);
                });
            }
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
