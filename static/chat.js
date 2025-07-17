// static/chat.js

const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const resetBtn = document.getElementById('reset-btn');

function appendMessage(role, text) {
  const div = document.createElement('div');
  div.classList.add('msg', role);
  div.textContent = text;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
  return div;
}

let typingEl = null;
function showTyping() {
  if (typingEl) return;
  typingEl = document.createElement('div');
  typingEl.classList.add('msg', 'ai', 'typing');
  typingEl.textContent = 'Em Tí đang suy nghĩ...';
  chatWindow.appendChild(typingEl);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}
function hideTyping() {
  if (!typingEl) return;
  typingEl.remove();
  typingEl = null;
}

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendMessage('user', text);
  chatInput.value = '';
  sendBtn.disabled = true;
  showTyping();

  try {
    const resp = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text })
    });
    const data = await resp.json();
    hideTyping();
    sendBtn.disabled = false;

    if (data.error) {
      appendMessage('system', 'Lỗi: ' + data.error);
      return;
    }

    appendMessage('ai', data.reply);
  } catch (err) {
    hideTyping();
    sendBtn.disabled = false;
    appendMessage('system', 'Lỗi mạng: ' + err.message);
  }
}

async function resetChat() {
  chatWindow.innerHTML = '';
  appendMessage('system', 'Đang reset hội thoại...');
  try {
    const resp = await fetch('/api/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reset: true })
    });
    const data = await resp.json();
    chatWindow.innerHTML = '';
    if (data.history) {
      data.history.forEach(m => appendMessage(m.role, m.content));
    } else {
      appendMessage('system', 'Đã reset.');
    }
  } catch (err) {
    appendMessage('system', 'Không reset được: ' + err.message);
  }
}

sendBtn.addEventListener('click', sendMessage);
resetBtn.addEventListener('click', resetChat);

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// Khi tải trang, lấy lịch sử ban đầu (system prompt)
(async function init() {
  try {
    const resp = await fetch('/api/reset', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reset: false })
    });
    const data = await resp.json();
    chatWindow.innerHTML = '';
    if (data.history) {
      data.history.forEach(m => appendMessage(m.role, m.content));
    }
  } catch {
    appendMessage('system', 'Không tải được lịch sử.');
  }
})();