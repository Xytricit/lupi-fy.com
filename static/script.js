
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

document.addEventListener('click', (e) => {
  // Toggle three-dot menus: add/remove 'open' class on container
  const moreBtn = e.target.closest('.more-btn');
  if (moreBtn) {
    const container = moreBtn.closest('.more-container');
    if (container) container.classList.toggle('open');
    return;
  }
  // Clicks outside any open more-container should close them
  if (!e.target.closest('.more-container')) {
    document.querySelectorAll('.more-container.open').forEach(c => c.classList.remove('open'));
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
      // hide the menu if open
      const container = reportBtn.closest('.more-container');
      if (container) {
        const menu = container.querySelector('.more-menu');
        if (menu) menu.style.display = 'none';
      }
    }).catch(err => console.warn(err));
    return;
  }

});

// main comment posting is handled in the inline template script to ensure DOM elements and CSRF are present

// Reply submissions are handled inline in the post_detail template to avoid duplicate handlers

// Toggle showing reply form
document.addEventListener('click', (ev) => {
  const btn = ev.target.closest('.comment-reply-btn');
  if (!btn) return;
  const parentId = btn.dataset.parentId;
  const form = document.querySelector(`.reply-form[data-parent-id='${parentId}']`);
  if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
});

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
