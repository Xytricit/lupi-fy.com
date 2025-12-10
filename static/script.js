
document.addEventListener("DOMContentLoaded", () => {
  const animatedElements = document.querySelectorAll(".fade-in-up, .fade-in-left, .fade-in-right, .fade-in-scale");

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add("visible");
      }
    });
  }, { threshold: 0.2 });

  animatedElements.forEach(el => observer.observe(el));
});

// --------------------------
// AJAX helpers + interactions
// --------------------------
function getCSRF() {
  const cookie = document.cookie.split(';').map(c => c.trim()).find(c => c.startsWith('csrftoken='));
  return cookie ? cookie.split('=')[1] : null;
}

function handleResponseJSON(res) {
  if (res.status === 401) {
    // Not authenticated — redirect to login preserving current path
    window.location.href = `/accounts/login/?next=${encodeURIComponent(window.location.pathname)}`;
    return Promise.reject(new Error('Authentication required'));
  }
  if (!res.ok) return res.json().then(j => Promise.reject(new Error(j && j.error ? j.error : 'Request failed')));
  return res.json();
}

// Debug: confirm the central script is loaded
try { console.debug('[static/script.js] loaded'); } catch(_) {}

document.addEventListener('click', (e) => {
  // Toggle three-dot menus: add/remove 'open' class on container
  const moreBtn = e.target.closest('.more-btn');
  if (moreBtn) {
    try { console.debug('[static/script.js] more-btn clicked'); } catch(_) {}
    const container = moreBtn.closest('.more-container');
    if (container) {
      const isOpen = container.classList.toggle('open');
      try { moreBtn.setAttribute('aria-expanded', isOpen ? 'true' : 'false'); } catch (_) {}
      // also explicitly show/hide the menu element in case template CSS isn't loaded
      const menu = container.querySelector('.more-menu');
      if (menu) {
        try {
          // position the menu below the button when opening
          if (isOpen) {
            menu.style.display = 'flex';
            try {
              // Move the menu into <body> and position absolutely using page coordinates.
              // This avoids transformed ancestors and stacking-context issues.
              const btnRect = moreBtn.getBoundingClientRect();
              menu.style.display = 'flex';
              menu.style.visibility = 'hidden';
              menu.style.zIndex = 9999;

              // remember original place so we can restore later
              if (!menu.__origParent) {
                menu.__origParent = menu.parentNode;
                menu.__nextSibling = menu.nextSibling;
              }

              // append to body (so absolute positioning is against the page)
              if (menu.parentNode !== document.body) document.body.appendChild(menu);

              // measure width then compute left so right aligns with button right
              const measuredWidth = menu.getBoundingClientRect().width || menu.offsetWidth || 160;
              const preferredLeft = btnRect.right - measuredWidth;
              const leftPx = Math.min(Math.max(8, preferredLeft + window.scrollX), window.innerWidth - measuredWidth - 8 + window.scrollX);

              // set absolute position using page (scroll) coordinates
              menu.style.position = 'absolute';
              menu.style.left = `${leftPx}px`;
              menu.style.top = `${btnRect.bottom + 6 + window.scrollY}px`;
              menu.style.right = '';
              menu.style.visibility = 'visible';
            } catch(_) {}
          } else {
            menu.style.display = 'none';
            try {
              // restore to original parent if we moved it
              if (menu.__origParent && menu.parentNode !== menu.__origParent) {
                if (menu.__nextSibling) menu.__origParent.insertBefore(menu, menu.__nextSibling);
                else menu.__origParent.appendChild(menu);
                menu.__origParent = null;
                menu.__nextSibling = null;
              }
              menu.style.top = '';
              menu.style.left = '';
              menu.style.position = '';
              menu.style.visibility = '';
              menu.style.zIndex = '';
            } catch(_) {}
          }
        } catch(_) {}
      }
    }
    return;
  }
  // Clicks outside any open more-container should close them
  if (!e.target.closest('.more-container')) {
    document.querySelectorAll('.more-container.open').forEach(c => {
      c.classList.remove('open');
      const btn = c.querySelector('.more-btn');
      if (btn) try { btn.setAttribute('aria-expanded', 'false'); } catch(_) {}
      // restore any moved .more-menu that originally belonged to this container
      try {
        // first try the simple case
        const menu = c.querySelector('.more-menu');
        if (menu) {
          menu.style.display = 'none';
          if (menu.__origParent && menu.parentNode !== menu.__origParent) {
            if (menu.__nextSibling) menu.__origParent.insertBefore(menu, menu.__nextSibling);
            else menu.__origParent.appendChild(menu);
            menu.__origParent = null;
            menu.__nextSibling = null;
          }
          menu.style.top = '';
          menu.style.left = '';
          menu.style.right = '';
          menu.style.position = '';
          menu.style.visibility = '';
          menu.style.zIndex = '';
        } else {
          // if not found inside container (it was moved to body), look for any .more-menu with stored origParent === this container
          document.querySelectorAll('.more-menu').forEach(m => {
            if (m.__origParent === c) {
              try { m.style.display = 'none'; } catch(_) {}
              try {
                if (m.parentNode !== m.__origParent) {
                  if (m.__nextSibling) m.__origParent.insertBefore(m, m.__nextSibling);
                  else m.__origParent.appendChild(m);
                }
                m.__origParent = null; m.__nextSibling = null;
                m.style.top = ''; m.style.left = ''; m.style.right = ''; m.style.position = ''; m.style.visibility = ''; m.style.zIndex = '';
              } catch(_) {}
            }
          });
        }
      } catch(_) {}
    });
  }
  // Bookmark toggle
  const bookmarkBtn = e.target.closest('.bookmark-btn');
  if (bookmarkBtn) {
    const postId = bookmarkBtn.dataset.postId;
    fetch(`/posts/post/${postId}/bookmark/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF() }
    }).then(handleResponseJSON).then(data => {
      if (data.bookmarked) {
        bookmarkBtn.classList.add('bookmarked');
      } else {
        bookmarkBtn.classList.remove('bookmarked');
      }
    }).catch(err => console.warn(err));
    return;
  }

  // Report post from more menu
  const reportBtn = e.target.closest('.report-post-btn');
  if (reportBtn) {
    const postId = reportBtn.dataset.postId;
    if (!confirm('Report this post for moderation?')) return;
    fetch(`/posts/post/${postId}/report/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF() }
    }).then(handleResponseJSON).then(data => {
      alert('Reported — thank you.');
      // close the menu by removing open class
      const container = reportBtn.closest('.more-container');
      if (container) {
        container.classList.remove('open');
        // restore moved menu if needed
        try {
          const menu = container.querySelector('.more-menu') || Array.from(document.querySelectorAll('.more-menu')).find(m => m.__origParent === container);
          if (menu) {
            menu.style.display = 'none';
            if (menu.__origParent && menu.parentNode !== menu.__origParent) {
              if (menu.__nextSibling) menu.__origParent.insertBefore(menu, menu.__nextSibling);
              else menu.__origParent.appendChild(menu);
            }
            menu.__origParent = null; menu.__nextSibling = null;
            menu.style.top = ''; menu.style.left = ''; menu.style.right = ''; menu.style.position = ''; menu.style.visibility = ''; menu.style.zIndex = '';
          }
        } catch(_) {}
      }
    }).catch(err => console.warn(err));
    return;
  }

  // Replies toggle: expand/collapse replies list when 'Replies (N)' clicked
  const repliesToggle = e.target.closest('.replies-toggle');
  if (repliesToggle) {
    try { console.debug('[static/script.js] replies-toggle clicked', repliesToggle.dataset); } catch(_) {}
    const parentId = repliesToggle.dataset.parentId;
    const replies = document.querySelector(`.replies[data-parent-id='${parentId}']`);
    // fallback: find replies within the same comment box
    const parentBox = repliesToggle.closest('.comment-box');
    const repliesEl = replies || (parentBox ? parentBox.querySelector('.replies') : null);
    if (!repliesEl) return;
    const isOpen = repliesEl.classList.toggle('open');
    repliesToggle.classList.toggle('open', isOpen);
    repliesEl.setAttribute('aria-hidden', !isOpen);
    // ensure replies are visible even if CSS isn't present
    try { repliesEl.style.display = isOpen ? 'block' : 'none'; } catch(_) {}
    return;
  }
});

// main comment posting is handled in the inline template script to ensure DOM elements and CSRF are present

// Reply submissions are handled inline in the post_detail template to avoid duplicate handlers

// Reply toggling is handled in the page's inline script (to support animation)

// Trending chips behaviour: filter main feed by selected chip
document.addEventListener('click', (ev) => {
  const chip = ev.target.closest('.trending-chip');
  if (!chip) return;
  const postId = chip.dataset.postId;
  const chips = document.querySelectorAll('.trending-chip');
  chips.forEach(c => c.classList.remove('active'));
  chip.classList.add('active');

  const posts = document.querySelectorAll('.main-feed .post-card');
  if (postId === 'all') {
    posts.forEach(p => p.style.display = 'block');
    return;
  }

  posts.forEach(p => {
    const pid = p.querySelector('.bookmark-btn') ? p.querySelector('.bookmark-btn').dataset.postId : null;
    if (pid === postId) p.style.display = 'block'; else p.style.display = 'none';
  });
});

// --------------------------
// User Profile Popup
// --------------------------
let activeProfilePopup = null;

document.addEventListener('click', async (e) => {
  // Close popup if clicking elsewhere
  if (!e.target.closest('.user-profile-trigger') && !e.target.closest('.profile-popup')) {
    if (activeProfilePopup) {
      activeProfilePopup.remove();
      activeProfilePopup = null;
    }
  }

  // Open profile popup on user pic click
  const userPfp = e.target.closest('.user-profile-trigger');
  if (!userPfp) return;

  // Close existing popup
  if (activeProfilePopup) {
    activeProfilePopup.remove();
  }

  const userId = userPfp.dataset.userId;
  const username = userPfp.dataset.username;
  const allowPublicSocials = userPfp.dataset.allowPublicSocials === 'true';

  try {
    const res = await fetch(`/accounts/user/${userId}/profile/`);
    if (!res.ok) throw new Error('Failed to load profile');

    const data = await res.json();

    // Create popup
    const popup = document.createElement('div');
    popup.className = 'profile-popup';
    popup.style.cssText = `
      position: fixed;
      background: white;
      border: 1px solid #ddd;
      border-radius: 12px;
      padding: 16px;
      width: 320px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: 'Inter', sans-serif;
    `;

    if (data.is_private) {
      popup.innerHTML = `
        <div style="text-align: center; color: #666;">
          <p style="margin: 0; font-weight: 600;">${username}</p>
          <p style="margin: 8px 0 0; font-size: 0.9rem; color: #999;">Account is private</p>
        </div>
      `;
    } else {
      popup.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 12px;">
          <div style="display: flex; align-items: center; gap: 12px;">
            ${data.avatar ? `<img src="${data.avatar}" alt="${username}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;">` : `<div style="width: 48px; height: 48px; border-radius: 50%; background: #e0e0e0;"></div>`}
            <div>
              <strong style="display: block;">${username}</strong>
              <span style="font-size: 0.85rem; color: #666;">${data.followers_count} followers</span>
            </div>
          </div>
          ${data.bio ? `<p style="margin: 0; font-size: 0.9rem; color: #555;">${data.bio}</p>` : ''}
          <button onclick="window.location.href='/accounts/user/${userId}/public-profile/'" class="view-account-btn" style="
            display: block;
            width: 100%;
            padding: 10px 16px;
            background: #1f9cee;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: 0.2s;
          ">View Profile</button>
        </div>
      `;
    }

    // Position below the pfp, keeping it on-screen
    const rect = userPfp.getBoundingClientRect();
    let left = rect.left - 140;
    let top = rect.bottom + 8;

    // Ensure popup stays within viewport horizontally
    if (left < 8) left = 8;
    if (left + 320 > window.innerWidth - 8) left = window.innerWidth - 320 - 8;

    // Ensure popup stays within viewport vertically
    if (top + 200 > window.innerHeight) {
      top = rect.top - 200 - 8;
    }

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;

    document.body.appendChild(popup);
    activeProfilePopup = popup;

    // Auto-close after 5 seconds
    setTimeout(() => {
      if (activeProfilePopup === popup) {
        popup.remove();
        activeProfilePopup = null;
      }
    }, 5000);

  } catch (err) {
    console.error('Profile fetch error:', err);
  }
});

// --------------------------
// Follow Button Handler
// --------------------------
document.addEventListener('click', async (e) => {
  const followBtn = e.target.closest('.follow-btn');
  if (!followBtn) return;

  const authorId = followBtn.dataset.authorId;
  if (!authorId) return;

  try {
    const res = await fetch(`/posts/users/${authorId}/follow/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF() }
    });

    if (!res.ok) throw new Error('Failed to follow/unfollow');

    const data = await res.json();
    followBtn.textContent = data.status;
    followBtn.classList.toggle('following', data.status === 'Following');

    // Update followers count if displayed
    const followersSpan = followBtn.parentElement?.querySelector('.followers-count');
    if (followersSpan && data.followers_count !== undefined) {
      followersSpan.textContent = `${data.followers_count} Followers`;
    }

  } catch (err) {
    console.error('Follow error:', err);
  }
});
