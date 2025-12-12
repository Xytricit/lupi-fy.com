/* ============================================================================
   CHATBOT INTERFACE JAVASCRIPT
   ============================================================================ */

class ChatBot {
  constructor() {
    this.messagesContainer = document.getElementById('chatMessages');
    this.messageInput = document.getElementById('messageInput');
    this.chatForm = document.getElementById('chatForm');
    this.taskButtons = document.getElementById('taskButtons');
    this.typingIndicator = document.getElementById('typingIndicator');
    this.clearChatBtn = document.getElementById('clearChatBtn');
    this.taskModal = document.getElementById('taskModal');

    this.init();
  }

  init() {
    // Event listeners
    this.chatForm.addEventListener('submit', (e) => this.handleSendMessage(e));
    this.clearChatBtn.addEventListener('click', () => this.clearChat());
    document.getElementById('taskCancelBtn').addEventListener('click', () => this.closeTaskModal());
    document.getElementById('taskConfirmBtn').addEventListener('click', () => this.executeConfirmedTask());

    // Load chat history on page load
    this.loadChatHistory();

    // Auto-focus input
    this.messageInput.focus();
  }

  // ========================================================================
  // MESSAGE HANDLING
  // ========================================================================

  async handleSendMessage(e) {
    e.preventDefault();

    const message = this.messageInput.value.trim();
    if (!message) return;

    // Clear input and focus
    this.messageInput.value = '';
    this.messageInput.focus();

    // Add user message to UI
    this.addMessage(message, 'user');

    // Show typing indicator
    this.showTypingIndicator(true);

    try {
      // Send message to backend
      const response = await fetch('/chatbot/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        body: JSON.stringify({ message })
      });

      const data = await response.json();

      if (data.success) {
        // Add assistant response
        this.addMessage(data.response, 'assistant');

        // Handle tasks if present
        if (data.tasks && data.tasks.length > 0) {
          this.displayTasks(data.tasks);
        }

        // Generate insights
        await this.updateInsights();
      } else {
        this.addMessage(`Error: ${data.error || 'Unknown error'}`, 'assistant');
      }
    } catch (error) {
      console.error('Chat error:', error);
      this.addMessage('Connection error. Make sure Ollama is running.', 'assistant');
    } finally {
      this.showTypingIndicator(false);
    }
  }

  addMessage(content, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Parse content for line breaks
    const paragraphs = content.split('\n').filter(p => p.trim());
    paragraphs.forEach(para => {
      const p = document.createElement('p');
      p.textContent = para;
      contentDiv.appendChild(p);
    });

    messageDiv.appendChild(contentDiv);
    this.messagesContainer.appendChild(messageDiv);

    // Auto-scroll to bottom
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  // ========================================================================
  // TASK EXECUTION
  // ========================================================================

  displayTasks(tasks) {
    this.taskButtons.innerHTML = '';

    tasks.forEach((task, index) => {
      const btn = document.createElement('button');
      btn.className = 'task-btn';
      btn.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
        </svg>
        ${task.label}
      `;

      btn.addEventListener('click', () => this.prepareTaskExecution(task));
      this.taskButtons.appendChild(btn);
    });
  }

  prepareTaskExecution(task) {
    // Store current task
    this.currentTask = task;

    // Show confirmation modal
    document.getElementById('taskModalTitle').textContent = task.label;
    document.getElementById('taskModalDescription').textContent = 
      `Execute: ${task.label}?`;

    this.openTaskModal();
  }

  async executeConfirmedTask() {
    const task = this.currentTask;
    this.closeTaskModal();

    try {
      switch (task.data.type || task.action) {
        case 'create_post':
        case 'blog':
          window.location.href = '/posts/create/';
          break;
        case 'community':
          window.location.href = '/communities/post/create/';
          break;
        case 'dashboard':
          window.location.href = '/dashboard/';
          break;
        case 'profile':
          window.location.href = '/accounts/dashboard/';
          break;
        case 'communities':
          window.location.href = '/communities/';
          break;
        default:
          // Try URL from task data
          if (task.data.url) {
            window.location.href = task.data.url;
          }
      }
    } catch (error) {
      console.error('Task execution error:', error);
      this.addMessage('Could not execute that action.', 'assistant');
    }
  }

  openTaskModal() {
    this.taskModal.classList.add('active');
  }

  closeTaskModal() {
    this.taskModal.classList.remove('active');
  }

  // ========================================================================
  // CHAT MANAGEMENT
  // ========================================================================

  async clearChat() {
    if (!confirm('Clear all messages? This cannot be undone.')) return;

    try {
      const response = await fetch('/chatbot/api/clear/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': this.getCsrfToken(),
        }
      });

      if (response.ok) {
        this.messagesContainer.innerHTML = `
          <div class="message assistant-message">
            <div class="message-content">
              <p>Chat cleared! Let's start fresh. What would you like to talk about?</p>
            </div>
          </div>
        `;
        this.taskButtons.innerHTML = '';
      }
    } catch (error) {
      console.error('Clear chat error:', error);
    }
  }

  async loadChatHistory() {
    try {
      const response = await fetch('/chatbot/api/history/');
      const data = await response.json();

      if (data.history && data.history.length > 0) {
        // Clear default greeting
        this.messagesContainer.innerHTML = '';

        // Add all messages from history
        data.history.forEach(msg => {
          this.addMessage(msg.content, msg.role);
        });
      }
    } catch (error) {
      console.error('Load history error:', error);
    }
  }

  // ========================================================================
  // INSIGHTS & ANALYTICS
  // ========================================================================

  async updateInsights() {
    try {
      const response = await fetch('/chatbot/api/analytics/');
      const data = response.json();

      if (data.analytics) {
        const insights = this.generateInsights(data.analytics, data.level);
        document.getElementById('insightText').textContent = insights;
      }
    } catch (error) {
      console.error('Analytics error:', error);
    }
  }

  generateInsights(analytics, level) {
    const insights = [];

    // Posts insight
    if (analytics.total_posts === 0) {
      insights.push('💡 Get started: Create your first post to begin building your audience.');
    } else if (analytics.blog_posts > analytics.community_posts) {
      insights.push('📝 You\'re strong with blog posts. Try community posts to expand your reach.');
    } else if (analytics.community_posts > analytics.blog_posts) {
      insights.push('🎯 Great community engagement! Diversify with blog posts for deeper content.');
    }

    // Engagement insight
    if (analytics.total_engagement < 10) {
      insights.push('🚀 Focus on content consistency to grow engagement.');
    } else if (analytics.engagement_score > analytics.total_posts * 2) {
      insights.push('⭐ Excellent engagement rate! Your content resonates well.');
    }

    // Community insight
    if (analytics.communities_joined < 3) {
      insights.push('🤝 Join more communities to discover new audiences.');
    }

    // Level insight
    if (level === 'Emerging Creator') {
      insights.push('📈 Create 5+ posts to reach Creator level.');
    } else if (level === 'Creator') {
      insights.push('🎖️ You\'re growing! 15+ posts unlocks Creator Plus.');
    } else if (level === 'Creator Plus') {
      insights.push('👑 Almost at Pro status. Keep the momentum going!');
    } else {
      insights.push('🏆 Creator Pro status achieved!');
    }

    return insights.slice(0, 3).join('\n');
  }

  // ========================================================================
  // UTILITIES
  // ========================================================================

  showTypingIndicator(show) {
    if (show) {
      this.typingIndicator.style.display = 'flex';
    } else {
      this.typingIndicator.style.display = 'none';
    }
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
}

// Initialize chatbot when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  new ChatBot();
});
