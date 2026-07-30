/**
 * AnuSathi — Frontend Application Logic
 * Connects to FastAPI backend at /upload and /query
 * Vanilla JS, no external framework dependencies.
 */

/* ============================================================
   CONFIGURATION
   ============================================================ */
const API_BASE = '';  // Same origin as the backend server

const UPLOAD_STEPS = [
  'Uploading paper...',
  'Extracting content...',
  'Generating embeddings...',
  'Indexing into Qdrant...',
  'Almost done...',
];

// Max time (ms) to wait for upload before aborting
const UPLOAD_TIMEOUT_MS = 5 * 60 * 1000; // 5 minutes

/* ============================================================
   STATE
   ============================================================ */
const state = {
  documentId: null,       // Active document_id from /upload
  filename: null,         // Display name of uploaded file
  isLoading: false,       // Waiting for /query response
  isUploading: false,     // Waiting for /upload response
  messageCount: 0,        // Track whether chat is empty
  activeQueryController: null, // AbortController for current /query fetch
};

/* ============================================================
   DOM REFERENCES
   ============================================================ */
const dom = {
  body: document.body,
  themeToggle: document.getElementById('theme-toggle'),
  themeIcon: document.getElementById('theme-icon'),

  homeBtn: document.getElementById('home-btn'),
  newChatBtn: document.getElementById('new-chat-btn'),

  sidebarToggle: document.getElementById('sidebar-toggle'),
  sidebar: document.getElementById('sidebar'),
  sidebarOverlay: document.getElementById('sidebar-overlay'),

  uploadDropzone: document.getElementById('upload-dropzone'),
  fileInput: document.getElementById('file-input'),
  browseBtn: document.getElementById('browse-btn'),
  dropzoneContent: document.getElementById('dropzone-content'),
  uploadProgress: document.getElementById('upload-progress'),
  progressMessage: document.getElementById('progress-message'),

  noPaperState: document.getElementById('no-paper-state'),
  activePaperState: document.getElementById('active-paper-state'),
  paperFilename: document.getElementById('paper-filename'),
  replacePaperBtn: document.getElementById('replace-paper-btn'),
  removePaperBtn: document.getElementById('remove-paper-btn'),

  chatMessages: document.getElementById('chat-messages'),
  welcomeScreen: document.getElementById('welcome-screen'),

  chatInput: document.getElementById('chat-input'),
  sendBtn: document.getElementById('send-btn'),
  stopBtn: document.getElementById('stop-btn'),

  toastContainer: document.getElementById('toast-container'),
};

/* ============================================================
   THEME MANAGEMENT
   ============================================================ */

/**
 * Apply theme to document and update icon
 */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);

  // Swap icon
  const icon = dom.themeIcon;
  icon.setAttribute('data-lucide', theme === 'dark' ? 'moon' : 'sun');
  lucide.createIcons();

  // Swap highlight.js theme
  const hljsTheme = document.getElementById('hljs-theme');
  if (hljsTheme) {
    hljsTheme.href = theme === 'dark'
      ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css'
      : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css';
  }
}

function initTheme() {
  const saved = localStorage.getItem('anusathi-theme') || 'dark';
  applyTheme(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  const next = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem('anusathi-theme', next);
  applyTheme(next);
}

/* ============================================================
   SIDEBAR MANAGEMENT
   ============================================================ */

function openSidebar() {
  dom.sidebar.classList.add('open');
  dom.sidebarOverlay.classList.add('visible');
  dom.sidebarOverlay.removeAttribute('aria-hidden');
}

function closeSidebar() {
  dom.sidebar.classList.remove('open');
  dom.sidebarOverlay.classList.remove('visible');
  dom.sidebarOverlay.setAttribute('aria-hidden', 'true');
}

function toggleSidebar() {
  if (dom.sidebar.classList.contains('open')) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

/* ============================================================
   TOAST NOTIFICATIONS
   ============================================================ */

/**
 * Show a toast notification
 * @param {string} message
 * @param {'success'|'error'|'info'} type
 * @param {number} duration ms before auto-dismiss
 */
function showToast(message, type = 'info', duration = 4000) {
  const iconMap = {
    success: 'check-circle',
    error: 'x-circle',
    info: 'info',
  };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.setAttribute('role', 'alert');
  toast.innerHTML = `
    <i data-lucide="${iconMap[type]}"></i>
    <span>${escapeHtml(message)}</span>
  `;

  dom.toastContainer.appendChild(toast);
  lucide.createIcons({ nodes: [toast] });

  // Auto-dismiss
  const timer = setTimeout(() => dismissToast(toast), duration);

  // Click to dismiss early
  toast.addEventListener('click', () => {
    clearTimeout(timer);
    dismissToast(toast);
  });
}

function dismissToast(toast) {
  toast.classList.add('leaving');
  toast.addEventListener('animationend', () => toast.remove(), { once: true });
}

/* ============================================================
   UPLOAD HANDLING
   ============================================================ */

/**
 * Continuously cycle through step messages while uploading.
 * Returns a cancel function to stop the loop.
 */
function startProgressAnimation() {
  let stepIndex = 0;
  let stopped = false;

  async function loop() {
    while (!stopped) {
      dom.progressMessage.textContent = UPLOAD_STEPS[stepIndex % UPLOAD_STEPS.length];
      stepIndex++;
      await delay(1800);
    }
  }

  loop();
  return () => { stopped = true; };
}

/**
 * Show upload progress UI inside dropzone.
 * Uses CSS classes so flexbox does not interfere with visibility.
 */
function showUploadProgress() {
  dom.dropzoneContent.classList.add('hidden');
  dom.uploadProgress.classList.remove('hidden');
  state.isUploading = true;
}

/**
 * Hide upload progress, restore dropzone content.
 */
function hideUploadProgress() {
  dom.dropzoneContent.classList.remove('hidden');
  dom.uploadProgress.classList.add('hidden');
  state.isUploading = false;
}

/**
 * Update the "Current Paper" section after upload
 */
function setActivePaper(documentId, filename) {
  state.documentId = documentId;
  state.filename = filename;

  dom.paperFilename.textContent = filename;
  dom.noPaperState.classList.add('hidden');
  dom.activePaperState.classList.remove('hidden');

  // Update chat input placeholder to reflect paper context
  dom.chatInput.placeholder = `Ask anything about "${filename}" or AI/ML in general...`;
}

/**
 * Clear the active paper
 */
function clearActivePaper() {
  state.documentId = null;
  state.filename = null;

  dom.noPaperState.classList.remove('hidden');
  dom.activePaperState.classList.add('hidden');

  dom.chatInput.placeholder = 'Ask anything about AI or your uploaded paper...';
}

/**
 * Handle a selected file — validate and upload
 */
async function handleFileSelected(file) {
  if (!file) return;

  // Validate by extension only (MIME types vary across OS/browser)
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('Only PDF files are allowed', 'error');
    return;
  }

  showUploadProgress();

  // Start cycling progress messages — stops when we call stopAnimation()
  const stopAnimation = startProgressAnimation();

  // AbortController lets us cancel the fetch if it takes too long
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), UPLOAD_TIMEOUT_MS);

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let detail = `Upload failed (HTTP ${response.status})`;
      try {
        const errJson = await response.json();
        if (errJson.detail) detail = errJson.detail;
      } catch (_) {
        const errText = await response.text().catch(() => '');
        if (errText) detail = errText;
      }
      throw new Error(detail);
    }

    const data = await response.json();

    if (data.status !== 'success') {
      throw new Error('Upload returned unexpected status');
    }

    setActivePaper(data.document_id, file.name);
    showToast('✓ Paper uploaded successfully', 'success');

    // Close sidebar on mobile after successful upload
    if (window.innerWidth <= 900) closeSidebar();

  } catch (err) {
    clearTimeout(timeoutId);
    console.error('[AnuSathi] Upload error:', err);
    if (err.name === 'AbortError') {
      showToast('Upload timed out. The server may be busy — please try again.', 'error');
    } else {
      showToast(`Upload failed: ${err.message}`, 'error');
    }
  } finally {
    stopAnimation();
    hideUploadProgress();
    // Reset file input so same file can be re-selected
    dom.fileInput.value = '';
  }
}

/* ============================================================
   CHAT RENDERING
   ============================================================ */

/**
 * Hide the welcome screen when first message is sent
 */
function hideWelcomeScreen() {
  if (dom.welcomeScreen) {
    dom.welcomeScreen.style.opacity = '0';
    dom.welcomeScreen.style.transition = 'opacity 200ms ease';
    setTimeout(() => {
      dom.welcomeScreen.remove();
    }, 200);
  }
}

/**
 * Render a user message bubble
 */
function appendUserMessage(text) {
  state.messageCount++;
  if (state.messageCount === 1) hideWelcomeScreen();

  const msg = document.createElement('div');
  msg.className = 'message user';
  msg.innerHTML = `<div class="message-bubble">${escapeHtml(text)}</div>`;
  dom.chatMessages.appendChild(msg);
  scrollToBottom();
}

/**
 * Show stop button, hide send button (while response is loading)
 */
function showStopBtn() {
  dom.stopBtn.classList.remove('hidden');
  dom.sendBtn.classList.add('hidden');
}

/**
 * Hide stop button, show send button
 */
function hideStopBtn() {
  dom.stopBtn.classList.add('hidden');
  dom.sendBtn.classList.remove('hidden');
}

/**
 * Stop the current in-flight query
 */
function stopResponse() {
  if (state.activeQueryController) {
    state.activeQueryController.abort();
    state.activeQueryController = null;
  }
}

/**
 * Reset to a fresh conversation: clear chat, restore welcome screen, clear paper
 */
function resetChat() {
  // Stop any in-flight request
  stopResponse();

  // Clear all messages and re-inject welcome screen
  dom.chatMessages.innerHTML = `
    <div class="welcome-screen" id="welcome-screen">
      <div class="welcome-content">
        <div class="welcome-icon" aria-hidden="true">
          <i data-lucide="book-open"></i>
        </div>
        <h1 class="welcome-title">AnuSathi</h1>
        <p class="welcome-subtitle">
          A Hinglish-friendly AI tutor that explains<br />AI/ML research papers in simple terms.
        </p>
        <p class="welcome-description">
          Upload a research paper to ask questions with citations,<br />
          or ask any AI/ML question directly.
        </p>
        <div class="welcome-chips" aria-label="Example questions">
          <button class="suggestion-chip" data-q="Explain attention mechanism in simple terms" type="button">
            Explain attention mechanism in simple terms
          </button>
          <button class="suggestion-chip" data-q="What is Retrieval Augmented Generation?" type="button">
            What is Retrieval Augmented Generation?
          </button>
          <button class="suggestion-chip" data-q="What is the difference between BERT and GPT?" type="button">
            BERT aur GPT mein kya fark hai?
          </button>
        </div>
      </div>
    </div>
  `;

  // Re-wire suggestion chips on the freshly injected DOM
  dom.chatMessages.querySelectorAll('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const question = chip.dataset.q;
      if (question && !state.isLoading) sendQuery(question);
    });
  });

  // Re-register welcome screen reference (used by hideWelcomeScreen)
  dom.welcomeScreen = dom.chatMessages.querySelector('#welcome-screen');

  // Reset state
  state.messageCount = 0;
  state.isLoading = false;
  clearActivePaper();
  setInputDisabled(false);
  hideStopBtn();

  // Reset textarea
  dom.chatInput.value = '';
  autoResizeTextarea();
  dom.chatInput.placeholder = 'Ask anything about AI or your uploaded paper...';

  lucide.createIcons({ nodes: [dom.chatMessages] });
  dom.chatInput.focus();
}
function appendTypingIndicator() {
  const wrapper = document.createElement('div');
  wrapper.className = 'message assistant';
  wrapper.id = 'typing-indicator-wrapper';
  wrapper.innerHTML = `
    <div class="typing-indicator">
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
      <span class="typing-dot"></span>
    </div>
  `;
  dom.chatMessages.appendChild(wrapper);
  scrollToBottom();
  return wrapper;
}

/**
 * Remove the typing indicator
 */
function removeTypingIndicator() {
  const el = document.getElementById('typing-indicator-wrapper');
  if (el) el.remove();
}

/**
 * Configure marked.js with highlight.js
 */
function configureMarked() {
  marked.setOptions({
    highlight: function (code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang }).value;
        } catch (_) {}
      }
      return hljs.highlightAuto(code).value;
    },
    breaks: true,
    gfm: true,
  });
}

/**
 * Render an assistant message with optional citations
 */
function appendAssistantMessage(answer, sources) {
  const wrapper = document.createElement('div');
  wrapper.className = 'message assistant';

  // Answer bubble
  const bubble = document.createElement('div');
  bubble.className = 'message-bubble';
  bubble.innerHTML = marked.parse(answer);
  wrapper.appendChild(bubble);

  dom.chatMessages.appendChild(wrapper);

  // Citation card (only if sources exist)
  if (sources && sources.length > 0) {
    const citationCard = buildCitationCard(sources);
    wrapper.appendChild(citationCard);
  }

  scrollToBottom();
}

/**
 * Build a grouped citation card element
 */
function buildCitationCard(sources) {
  // Group pages by document_id
  const grouped = {};
  for (const src of sources) {
    const key = src.document_id || 'Unknown Document';
    if (!grouped[key]) grouped[key] = new Set();
    if (src.page !== undefined && src.page !== null) {
      grouped[key].add(src.page);
    }
  }

  const card = document.createElement('div');
  card.className = 'citation-card';

  let html = `<div class="citation-title">Sources</div>`;

  for (const [docId, pages] of Object.entries(grouped)) {
    const sortedPages = [...pages].sort((a, b) => a - b);
    const pageBadges = sortedPages
      .map(p => `<span class="citation-page-badge">${p}</span>`)
      .join('');

    html += `
      <div class="citation-entry">
        <span class="citation-file-icon"><i data-lucide="file-text"></i></span>
        <div class="citation-details">
          <span class="citation-filename">${escapeHtml(docId)}</span>
          <span class="citation-pages">
            Pages:&nbsp;${pageBadges || '<span class="citation-page-badge">—</span>'}
          </span>
        </div>
      </div>
    `;
  }

  card.innerHTML = html;
  lucide.createIcons({ nodes: [card] });
  return card;
}

/* ============================================================
   QUERY HANDLING
   ============================================================ */

/**
 * Send question to /query API
 */
async function sendQuery(question) {
  if (state.isLoading) return;
  if (!question.trim()) {
    showToast('Please type a question first', 'error');
    return;
  }

  state.isLoading = true;
  setInputDisabled(true);
  showStopBtn();

  appendUserMessage(question);
  const typingEl = appendTypingIndicator();

  // Create a fresh AbortController for this request
  const controller = new AbortController();
  state.activeQueryController = controller;

  try {
    const payload = { q: question };
    if (state.documentId) {
      payload.document_id = state.documentId;
    }

    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => '');
      throw new Error(errText || `Query failed (HTTP ${response.status})`);
    }

    const data = await response.json();

    removeTypingIndicator();
    appendAssistantMessage(data.answer, data.sources);

  } catch (err) {
    removeTypingIndicator();
    if (err.name === 'AbortError') {
      // User deliberately stopped — show a subtle stopped message
      const stopped = document.createElement('div');
      stopped.className = 'message assistant';
      stopped.innerHTML = '<div class="message-bubble stopped-msg"><i data-lucide="octagon-x" style="width:14px;height:14px;display:inline;vertical-align:middle;margin-right:6px;"></i>Response stopped.</div>';
      dom.chatMessages.appendChild(stopped);
      lucide.createIcons({ nodes: [stopped] });
      scrollToBottom();
    } else {
      console.error('[AnuSathi] Query error:', err);
      appendAssistantMessage(
        `Sorry, something went wrong. Please try again.\n\n*${escapeHtml(err.message)}*`,
        null
      );
      showToast('Request failed. Please check your connection.', 'error');
    }
  } finally {
    state.isLoading = false;
    state.activeQueryController = null;
    setInputDisabled(false);
    hideStopBtn();
    dom.chatInput.focus();
  }
}

/* ============================================================
   INPUT AREA
   ============================================================ */

/**
 * Enable / disable the input and send button
 */
function setInputDisabled(disabled) {
  dom.chatInput.disabled = disabled;
  dom.sendBtn.disabled = disabled;
}

/**
 * Auto-grow textarea height
 */
function autoResizeTextarea() {
  const ta = dom.chatInput;
  ta.style.height = 'auto';
  ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
}

/**
 * Scroll the chat to the bottom
 */
function scrollToBottom() {
  dom.chatMessages.scrollTop = dom.chatMessages.scrollHeight;
}

/* ============================================================
   UTILITIES
   ============================================================ */

/**
 * Escape HTML to prevent XSS in non-markdown content
 */
function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Simple promise-based delay
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/* ============================================================
   EVENT LISTENERS
   ============================================================ */

function attachEventListeners() {
  // ---- Theme toggle ----
  dom.themeToggle.addEventListener('click', toggleTheme);

  // ---- Home (brand click) ----
  dom.homeBtn.addEventListener('click', resetChat);

  // ---- New Chat ----
  dom.newChatBtn.addEventListener('click', resetChat);

  // ---- Stop button ----
  dom.stopBtn.addEventListener('click', stopResponse);

  // ---- Sidebar toggle ----
  dom.sidebarToggle.addEventListener('click', toggleSidebar);
  dom.sidebarOverlay.addEventListener('click', closeSidebar);

  // ---- Upload: browse button ----
  dom.browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    if (!state.isUploading) dom.fileInput.click();
  });

  // ---- Upload: dropzone click ----
  dom.uploadDropzone.addEventListener('click', () => {
    if (!state.isUploading) dom.fileInput.click();
  });

  // ---- Upload: keyboard access ----
  dom.uploadDropzone.addEventListener('keydown', (e) => {
    if ((e.key === 'Enter' || e.key === ' ') && !state.isUploading) {
      e.preventDefault();
      dom.fileInput.click();
    }
  });

  // ---- Upload: file input change ----
  dom.fileInput.addEventListener('change', (e) => {
    handleFileSelected(e.target.files[0]);
  });

  // ---- Upload: drag and drop ----
  dom.uploadDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!state.isUploading) dom.uploadDropzone.classList.add('drag-over');
  });

  dom.uploadDropzone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dom.uploadDropzone.classList.remove('drag-over');
  });

  dom.uploadDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dom.uploadDropzone.classList.remove('drag-over');
    if (!state.isUploading) {
      const file = e.dataTransfer.files[0];
      handleFileSelected(file);
    }
  });

  // ---- Paper actions ----
  dom.replacePaperBtn.addEventListener('click', () => {
    if (!state.isUploading) dom.fileInput.click();
  });

  dom.removePaperBtn.addEventListener('click', () => {
    clearActivePaper();
    showToast('Paper removed', 'info');
  });

  // ---- Chat input: auto-resize ----
  dom.chatInput.addEventListener('input', autoResizeTextarea);

  // ---- Chat input: send on Enter (not Shift+Enter) ----
  dom.chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  // ---- Send button ----
  dom.sendBtn.addEventListener('click', handleSend);

  // ---- Suggestion chips ----
  document.querySelectorAll('.suggestion-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const question = chip.dataset.q;
      if (question && !state.isLoading) {
        sendQuery(question);
      }
    });
  });
}

/**
 * Handle send action
 */
function handleSend() {
  const question = dom.chatInput.value.trim();
  if (!question) {
    showToast('Please type a question first', 'error');
    return;
  }
  dom.chatInput.value = '';
  autoResizeTextarea();
  sendQuery(question);
}

/* ============================================================
   INITIALIZATION
   ============================================================ */

function init() {
  // Apply saved theme preference
  initTheme();

  // Configure markdown renderer
  configureMarked();

  // Initialize Lucide icons
  lucide.createIcons();

  // Attach all event listeners
  attachEventListeners();

  // Focus the chat input
  dom.chatInput.focus();
}

// Boot when DOM is ready
document.addEventListener('DOMContentLoaded', init);
