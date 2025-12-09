
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

document.addEventListener('click', (e) => {
  // Toggle three-dot menus
  const moreBtn = e.target.closest('.more-btn');
  if (moreBtn) {
    const container = moreBtn.closest('.more-container');
    const menu = container.querySelector('.more-menu');
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
    return;
  }
  // Bookmark toggle
  const bookmarkBtn = e.target.closest('.bookmark-btn');
  if (bookmarkBtn) {
    const postId = bookmarkBtn.dataset.postId;
    fetch(`/posts/post/${postId}/bookmark/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF() }
    }).then(r => r.json()).then(data => {
      if (data.bookmarked) {
        bookmarkBtn.classList.add('bookmarked');
      } else {
        bookmarkBtn.classList.remove('bookmarked');
      }
    });
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
    }).then(r => r.json()).then(data => {
      alert('Reported — thank you.');
    });
    return;
  }

});

// Comment posting (main form)
const commentForm = document.getElementById('commentForm');
if (commentForm) {
  commentForm.addEventListener('submit', (ev) => {
    ev.preventDefault();
    const postId = commentForm.dataset.postId;
    const text = commentForm.querySelector('textarea[name="text"]').value.trim();
    if (!text) return alert('Comment cannot be empty.');

    fetch(`/posts/post/${postId}/comment/`, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `text=${encodeURIComponent(text)}`
    }).then(r => r.json()).then(data => {
      if (data.error) return alert(data.error);
      // prepend new comment
      const list = document.getElementById('commentsList');
      const node = document.createElement('div');
      node.className = 'comment-box';
      node.innerHTML = `<div class="comment-header"><strong>${data.user}</strong><span class="comment-date">${data.created_at}</span></div><p class="comment-content">${data.text}</p>`;
      list.prepend(node);
      commentForm.querySelector('textarea[name="text"]').value = '';
    });
  });
}

// Reply forms: delegate submit
document.addEventListener('submit', (ev) => {
  const form = ev.target.closest('.reply-form');
  if (!form) return;
  ev.preventDefault();
  const parentId = form.dataset.parentId;
  const text = form.querySelector('textarea[name="text"]').value.trim();
  const postId = document.getElementById('commentForm') ? document.getElementById('commentForm').dataset.postId : null;
  if (!text) return alert('Reply cannot be empty.');
  fetch(`/posts/post/${postId}/comment/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCSRF(), 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `text=${encodeURIComponent(text)}&parent_id=${parentId}`
  }).then(r => r.json()).then(data => {
    if (data.error) return alert(data.error);
    // append reply into replies container
    const parentBox = document.querySelector(`[data-comment-id='${parentId}']`);
    const replies = parentBox.querySelector('.replies');
    const node = document.createElement('div');
    node.className = 'comment-box reply-box';
    node.innerHTML = `<div class="comment-header"><strong>${data.user}</strong><span class="comment-date">${data.created_at}</span></div><p class="comment-content">${data.text}</p>`;
    replies.appendChild(node);
    form.style.display = 'none';
    form.querySelector('textarea[name="text"]').value = '';
  });
});

// Toggle showing reply form
document.addEventListener('click', (ev) => {
  const btn = ev.target.closest('.comment-reply-btn');
  if (!btn) return;
  const parentId = btn.dataset.parentId;
  const form = document.querySelector(`.reply-form[data-parent-id='${parentId}']`);
  if (form) form.style.display = form.style.display === 'none' ? 'block' : 'none';
});
