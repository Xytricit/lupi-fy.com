
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

function csrfToken() {
  return getCSRF();
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

// --------------------------
// WebSocket for DM notifications
// --------------------------
let dmSocket = null;
const currentUserMeta = document.querySelector('meta[name="current-user-id"]');
if (currentUserMeta) {
  const currentUserId = currentUserMeta.getAttribute('content');
  const wsScheme = (location.protocol === 'https:') ? 'wss:' : 'ws:';
  try {
    dmSocket = new WebSocket(`${wsScheme}//${location.host}/ws/dm/${currentUserId}/`);
    dmSocket.addEventListener('open', () => console.debug('DM socket open'));
    dmSocket.addEventListener('close', () => console.debug('DM socket closed'));
    dmSocket.addEventListener('message', (ev) => {
      try {
        const data = JSON.parse(ev.data);
        if (data.type === 'dm.message' && data.message) {
          const msg = data.message;
          // show small toast notification
          try {
            const toast = document.createElement('div');
            toast.className = 'dm-toast';
            toast.style.cssText = 'position:fixed;right:16px;bottom:16px;padding:12px 16px;background:#0ea5a4;color:#fff;border-radius:10px;z-index:20000;box-shadow:0 8px 30px rgba(0,0,0,0.12);';
            toast.textContent = `${msg.sender}: ${msg.content.slice(0,120)}`;
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 4000);
          } catch (_) {}

          // append to open popup if it matches
          if (activeProfilePopup) {
            const thread = activeProfilePopup.querySelector('.chat-thread');
            if (thread) {
              const bubble = document.createElement('div');
              bubble.style.cssText = 'padding:8px 10px;border-radius:10px;margin-bottom:6px;background:#eef2ff;color:#041624;max-width:80%;';
              bubble.textContent = `${msg.sender}: ${msg.content}`;
              thread.appendChild(bubble);
              thread.scrollTop = thread.scrollHeight;
            }
          }
        }
        // handle user block/unblock events
        if (data.type === 'user.block' && data.payload) {
          const p = data.payload;
          try {
            const myId = currentUserId;
            const byId = String(p.by_user_id);
            const targetId = String(p.target_user_id);
            const action = p.action; // 'blocked' or 'unblocked'

            // If current user is involved, update UI
            if (myId === byId || myId === targetId) {
              // If block affects the currently open chat, disable composer and hide messages from blocked user
              const chatMain = document.getElementById('chat-main');
              if (chatMain) {
                const otherId = document.querySelector('.conversation-item.active') ? document.querySelector('.conversation-item.active').dataset.userId : null;
                // also check URL selected user id on chat page
                const sel = window.location.pathname.match(/\/accounts\/chat\/(\d+)\//) || window.location.pathname.match(/\/accounts\/chat\/(\d+)$/);
                const selectedUserId = sel ? sel[1] : null;
                const affectedUser = (myId === byId) ? targetId : byId;
                if (selectedUserId && (selectedUserId === affectedUser || selectedUserId === byId || selectedUserId === targetId)) {
                  // remove messages from blocked user
                  document.querySelectorAll('#message-thread div').forEach(d => {
                    try {
                      if (d.textContent && d.textContent.includes(` ${affectedUser}: `)) d.remove();
                    } catch(_) {}
                  });
                  // disable composer if the other user blocked you or you blocked them
                  const input = document.getElementById('message-input');
                  const form = document.getElementById('message-form');
                  if (input && form) {
                    if (action === 'blocked') {
                      input.disabled = true;
                      form.querySelector('button[type=submit]').disabled = true;
                      // show banner
                      let banner = document.getElementById('blockBanner');
                      if (!banner) {
                        banner = document.createElement('div');
                        banner.id = 'blockBanner';
                        banner.style.cssText = 'padding:10px;background:#fff3f2;color:#7f1d1d;border:1px solid #fecaca;border-radius:8px;margin-bottom:8px;';
                        banner.textContent = 'This conversation is blocked. Messaging is disabled.';
                        const container = document.getElementById('chat-main');
                        if (container) container.insertBefore(banner, container.firstChild);
                      }
                    } else if (action === 'unblocked') {
                      input.disabled = false;
                      form.querySelector('button[type=submit]').disabled = false;
                      const banner = document.getElementById('blockBanner'); if (banner) banner.remove();
                    }
                  }
                }
              }
            }
          } catch (e) { console.error('Failed to handle block event', e); }
        }
      } catch (err) { console.error('WS msg parse', err); }
    });
  } catch (err) {
    console.warn('DM WebSocket creation failed', err);
  }
}

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

  // Chat from options menu: navigate to chat page
  const chatMenuBtn = e.target.closest('.chat-menu-btn');
  if (chatMenuBtn) {
    const authorId = chatMenuBtn.dataset.authorId;
    if (authorId) {
      window.location.href = `/accounts/chat/${authorId}/`;
    }
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
  try {
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
  } catch (err) {
    console.error('Error handling trending chip click:', err);
  }
});

// --------------------------
// User Profile Popup
// --------------------------
let activeProfilePopup = null;

document.addEventListener('click', async (e) => {
  // If this click originated from a post-author specific avatar, let the
  // page-level handler manage it (we show a small dropdown). Avoid opening
  // the global profile popup in that case.
  if (e.target.closest && e.target.closest('.author-avatar-trigger')) return;
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
      background: var(--card-bg);
      border: 1px solid #ddd;
      border-radius: 12px;
      padding: 16px;
      width: 320px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
      z-index: 10000;
      font-family: 'Inter', sans-serif;
    `;

    // Always render a full structured popup so Social/Achievements/Chat sections are present
    const socials = data.socials || {};
    const achievements = data.achievements || [];

    function socialLine(key, label) {
      const val = socials[key];
      if (val) return `<div style="font-size:0.9rem; color:#333;">${label}: <a href="${val}" target="_blank" style="color:#1f9cee;">${val}</a></div>`;
      if (data.allow_public_socials === false) return `<div style="font-size:0.9rem; color:#999;">${label}: Hidden</div>`;
      return `<div style="font-size:0.9rem; color:#999;">${label}: —</div>`;
    }

    popup.innerHTML = `
      <div style="display:flex;flex-direction:column;gap:12px;">
        ${data.is_private && !data.is_own_profile ? `<div style="padding:8px;border-radius:8px;background:#fff7ed;border:1px solid #ffedd5;color:#92400e;font-weight:600;">This user has set their profile to private — some sections are hidden.</div>` : ''}
        <div style="display:flex;align-items:center;gap:12px;">
          ${data.avatar ? `<img src="${data.avatar}" alt="${username}" style="width:48px;height:48px;border-radius:50%;object-fit:cover;">` : `<div style="width:48px;height:48px;border-radius:50%;background:#e0e0e0;"></div>`}
          <div>
            <strong style="display:block;">${username}</strong>
            <span style="font-size:0.85rem;color:#666;">${data.followers_count || 0} followers</span>
          </div>
        </div>

        ${data.bio ? `<p style="margin:0;font-size:0.9rem;color:#555;">${data.bio}</p>` : `<p style="margin:0;font-size:0.9rem;color:#999;">No bio provided</p>`}

        <div class="profile-actions" style="display:flex;gap:8px;">
          <button class="view-account-btn" data-userid="${userId}" style="flex:1;padding:10px;background:#1f9cee;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;">View Profile</button>
          ${data.allow_dms === false && !data.is_own_profile ?
            `<button class="chat-account-btn" data-userid="${userId}" disabled style="flex:1;padding:10px;background:#94a3b8;color:#fff;border:none;border-radius:8px;cursor:not-allowed;font-weight:600;">Chat (disabled)</button>` :
            `<button class="chat-account-btn" data-userid="${userId}" style="flex:1;padding:10px;background:#2dd4bf;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;">Chat</button>`
          }
        </div>

        <div class="profile-section socials" style="border-top:1px solid #f0f0f0;padding-top:8px;">
          <strong style="font-size:0.9rem;display:block;margin-bottom:6px;color:#333;">Social</strong>
          ${socialLine('youtube','YouTube')}
          ${socialLine('instagram','Instagram')}
          ${socialLine('tiktok','TikTok')}
          ${socialLine('twitch','Twitch')}
          ${socialLine('github','GitHub')}
        </div>

        <div class="profile-section achievements" style="border-top:1px solid #f0f0f0;padding-top:8px;">
          <strong style="font-size:0.9rem;display:block;margin-bottom:6px;color:#333;">Achievements</strong>
          ${achievements.length ? achievements.map(a => `<div style="font-size:0.9rem;color:#333;">${a}</div>`).join('') : '<div style="font-size:0.9rem;color:#999;">No achievements</div>'}
        </div>

        <div class="profile-section chat" style="border-top:1px solid #f0f0f0;padding-top:8px;">
          <strong style="font-size:0.9rem;display:block;margin-bottom:6px;color:#333;">Chat</strong>
          <div style="font-size:0.9rem;color:#666;">Start a private conversation with ${username}.</div>
        </div>
      </div>
    `;

    // wire up View Profile button
    popup.querySelectorAll('.view-account-btn').forEach(btn => {
      btn.addEventListener('click', (ev) => {
        const id = btn.dataset.userid || userId;
        // Always go to public profile page
        window.location.href = `/accounts/user/${id}/public-profile/`;
      });
    });
    });

    // wire up Chat button: navigate to full chat page
    popup.querySelectorAll('.chat-account-btn').forEach(btn => {
      btn.addEventListener('click', (ev) => {
        const id = btn.dataset.userid || userId;
        window.location.href = `/accounts/chat/${id}/`;
      });
    });

    // Position below the pfp, keeping it on-screen
    const rect = userPfp.getBoundingClientRect();
    let left = rect.left - 140;
    let top = rect.bottom + 8;

    // Ensure popup stays within viewport horizontally
    if (left < 8) left = 8;
    if (left + 320 > window.innerWidth - 8) left = window.innerWidth - 320 - 8;

    // Ensure popup stays within viewport vertically
    // Reserve space for popup; when it has chat thread + composer it can be ~500px tall
    const estimatedPopupHeight = 500;
    const viewportBottom = window.innerHeight - 20; // 20px margin from bottom
    if (top + estimatedPopupHeight > viewportBottom) {
      // Try positioning above
      const topAbove = rect.top - estimatedPopupHeight - 8;
      if (topAbove >= 20) {
        top = topAbove;
      } else {
        // Not enough space above either; position below but add max-height and overflow
        top = rect.bottom + 8;
      }
    }

    popup.style.left = `${left}px`;
    popup.style.top = `${top}px`;
    
    // Add max-height and overflow scrolling to ensure popup doesn't overflow viewport
    popup.style.maxHeight = `${Math.max(300, window.innerHeight - top - 20)}px`;
    popup.style.overflowY = 'auto';
    popup.style.overflowX = 'hidden';

    document.body.appendChild(popup);
    activeProfilePopup = popup;

    // Defensive: ensure Chat button exists even if popup HTML rendering missed it
    try {
      const actions = popup.querySelector('.profile-actions');
      if (actions && !actions.querySelector('.chat-account-btn')) {
        const chatBtn = document.createElement('button');
        chatBtn.className = 'chat-account-btn';
        chatBtn.dataset.userid = userId;
        if (data.allow_dms === false && !data.is_own_profile) {
          chatBtn.disabled = true;
          chatBtn.textContent = 'Chat (disabled)';
          chatBtn.style.cssText = 'flex:1;padding:10px;background:#94a3b8;color:#fff;border:none;border-radius:8px;cursor:not-allowed;font-weight:600;';
        } else {
          chatBtn.textContent = 'Chat';
          chatBtn.style.cssText = 'flex:1;padding:10px;background:#2dd4bf;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;';
        }
        actions.appendChild(chatBtn);
        // attach same handler
        chatBtn.addEventListener('click', async (ev) => {
          // forward to existing handler by triggering click on any existing one
          const existing = popup.querySelector('.chat-account-btn');
          if (existing && existing !== chatBtn) existing.click();
        });
      }
    } catch (err) { console.warn('profile popup: chat button ensure failed', err); }

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

  // Allow multiple attribute names used across templates: data-author-id, data-user-id, data-userid
  const authorId = followBtn.dataset.authorId || followBtn.dataset.userId || followBtn.dataset.userid || followBtn.getAttribute('data-author-id') || followBtn.getAttribute('data-user-id');
  if (!authorId) {
    console.warn('[static/script.js] follow-btn clicked but no author/user id found on element', followBtn);
    return;
  }

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
