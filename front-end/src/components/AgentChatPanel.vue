<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import DOMPurify from 'dompurify'

const props = defineProps<{
  templateId?: string | null
  templateName?: string | null
  structureName?: string | null
}>()

interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
}

let nextMsgId = 0
const messages = ref<ChatMessage[]>([])
const userInput = ref('')
const streaming = ref(false)
const connected = ref(false)
const connecting = ref(false)
const modelName = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

const route = useRoute()

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null
let currentTemplateId: string | null = null

function buildWsUrl(): string {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  let url = `${proto}//${window.location.host}/api/v1/agent/ws`
  if (currentTemplateId) {
    url += `?template_id=${currentTemplateId}`
  }
  return url
}

function connect() {
  if (connecting.value || (ws && ws.readyState === WebSocket.OPEN)) return
  disconnect()
  connecting.value = true

  const url = buildWsUrl()
  ws = new WebSocket(url)

  ws.onopen = () => {
    connected.value = true
    connecting.value = false
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)

    if (msg.type === 'connected') {
      modelName.value = msg.model || ''
      return
    }

    if (msg.type === 'delta') {
      const last = messages.value[messages.value.length - 1]
      if (last && last.role === 'assistant') {
        last.content += msg.content
      } else {
        messages.value.push({ id: nextMsgId++, role: 'assistant', content: msg.content })
      }
      scrollToBottom()
      return
    }

    if (msg.type === 'done') {
      streaming.value = false
      scrollToBottom()
      return
    }

    if (msg.type === 'response') {
      messages.value.push({ id: nextMsgId++, role: 'assistant', content: msg.content })
      streaming.value = false
      scrollToBottom()
      return
    }

    if (msg.type === 'error') {
      messages.value.push({ id: nextMsgId++, role: 'assistant', content: `**Error:** ${msg.message}` })
      streaming.value = false
    }
  }

  ws.onclose = () => {
    connected.value = false
    connecting.value = false
  }

  ws.onerror = () => {
    connected.value = false
    connecting.value = false
  }
}

function disconnect() {
  if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
  if (ws) {
    ws.onclose = null
    ws.onerror = null
    ws.close()
    ws = null
  }
  connected.value = false
  connecting.value = false
}

function sendMessage() {
  if (!userInput.value.trim()) return

  if (!ws || ws.readyState !== WebSocket.OPEN) {
    connect()
    const content = userInput.value.trim()
    const waitForOpen = () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        doSend(content)
      } else {
        reconnectTimer = setTimeout(waitForOpen, 100)
      }
    }
    reconnectTimer = setTimeout(waitForOpen, 200)
    return
  }

  doSend(userInput.value.trim())
}

function doSend(content: string) {
  messages.value.push({ id: nextMsgId++, role: 'user', content })
  userInput.value = ''
  streaming.value = true

  ws!.send(JSON.stringify({
    type: 'message',
    content,
    stream: true,
  }))

  scrollToBottom()
}

function clearChat() {
  messages.value = []
  disconnect()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// When template changes, reconnect with new context (only if already connected)
watch(() => props.templateId, (newId) => {
  const changed = newId !== currentTemplateId
  currentTemplateId = newId ?? null
  if (changed && connected.value) {
    disconnect()
    connect()
  }
})

// Clear chat history whenever the user navigates to a different page
watch(() => route.path, () => {
  clearChat()
})

onMounted(() => {
  currentTemplateId = props.templateId ?? null
  connect()
})

onUnmounted(() => { disconnect() })

const hasContext = computed(() => !!props.templateId)

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function renderInline(text: string): string {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}

function renderMarkdown(text: string): string {
  const parts: string[] = []
  let lastIndex = 0
  const codeBlockRe = /```(\w*)\n?([\s\S]*?)```/g
  let match: RegExpExecArray | null

  while ((match = codeBlockRe.exec(text)) !== null) {
    parts.push(renderInline(text.slice(lastIndex, match.index)))
    const lang = match[1] || ''
    const code = escapeHtml(match[2].replace(/\n$/, ''))
    parts.push(
      `<div class="code-block-wrapper">` +
      `<div class="code-block-actions">` +
      `<button class="copy-code-btn" title="Copy to clipboard">Copy</button>` +
      `<button class="replace-code-btn" title="Replace template content">Replace</button>` +
      `</div><pre><code${lang ? ` class="language-${lang}"` : ''}>${code}</code></pre></div>`
    )
    lastIndex = match.index + match[0].length
  }

  parts.push(renderInline(text.slice(lastIndex)))
  return DOMPurify.sanitize(parts.join(''))
}

function handleChatClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  const wrapper = target.closest('.code-block-wrapper')
  if (!wrapper) return
  const code = (wrapper.querySelector('code') as HTMLElement | null)?.innerText ?? ''
  if (target.classList.contains('copy-code-btn')) {
    navigator.clipboard.writeText(code).then(() => {
      target.textContent = 'Copied!'
      setTimeout(() => { target.textContent = 'Copy' }, 2000)
    })
  } else if (target.classList.contains('replace-code-btn')) {
    window.dispatchEvent(new CustomEvent('replace-template-content', { detail: code }))
  }
}
</script>

<template>
  <div class="agent-chat-panel d-flex flex-column h-100">
    <div class="chat-header d-flex justify-content-between align-items-center px-3 py-2">
      <div class="d-flex align-items-center gap-2">
        <i class="bi bi-robot text-primary"></i>
        <span class="fw-semibold small">AI Assistant</span>
        <span v-if="connected" class="badge bg-success" style="font-size:0.6rem">Connected</span>
        <span v-else-if="connecting" class="badge bg-warning text-dark" style="font-size:0.6rem">Connecting...</span>
        <span v-else class="badge bg-secondary" style="font-size:0.6rem">Disconnected</span>
      </div>
      <div class="d-flex gap-1">
        <button v-if="!connected && !connecting" class="btn btn-sm btn-outline-primary" @click="connect" title="Reconnect">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <button class="btn btn-sm btn-outline-secondary" @click="clearChat" title="Clear chat">
          <i class="bi bi-trash"></i>
        </button>
      </div>
    </div>

    <div v-if="hasContext" class="context-banner px-3 py-2">
      <div class="d-flex align-items-center gap-1 mb-1">
        <i class="bi bi-lightning-charge-fill"></i>
        <span class="small fw-semibold">Context-aware</span>
      </div>
      <div class="context-pills">
        <span class="context-pill"><i class="bi bi-file-code me-1"></i>{{ templateName || 'Template' }}</span>
        <span class="context-pill"><i class="bi bi-diagram-3 me-1"></i>{{ structureName || 'Structure' }}</span>
      </div>
      <div class="small mt-1" style="font-size:0.7rem;opacity:0.8;">Knows your data fields, SQL query and current template HTML</div>
    </div>
    <div v-else class="context-banner context-banner-generic px-3 py-1">
      <i class="bi bi-info-circle me-1"></i>
      <span class="small">Select a template to enable context-aware help</span>
    </div>

    <div
      class="chat-messages flex-grow-1"
      ref="messagesContainer"
      role="log"
      aria-label="AI assistant conversation"
      aria-live="polite"
      @click="handleChatClick"
    >
      <div v-if="messages.length === 0" class="empty-chat text-center text-muted py-5">
        <i class="bi bi-chat-dots" style="font-size: 2rem;"></i>
        <p class="mt-2 small">Ask me about Mustache templates or report layout</p>
      </div>
      <div v-for="msg in messages" :key="msg.id" class="chat-message" :class="msg.role">
        <div class="message-avatar">
          <i :class="msg.role === 'user' ? 'bi bi-person-fill' : 'bi bi-robot'"></i>
        </div>
        <div class="message-bubble" v-html="renderMarkdown(msg.content)"></div>
      </div>
      <div v-if="streaming" class="chat-message assistant">
        <div class="message-avatar"><i class="bi bi-robot"></i></div>
        <div class="message-bubble"><span class="typing-indicator"><span></span><span></span><span></span></span></div>
      </div>
    </div>

    <div class="chat-input px-3 py-2">
      <div class="input-group input-group-sm">
        <input
          v-model="userInput"
          type="text"
          class="form-control"
          placeholder="Ask about Mustache or layout..."
          aria-label="Message to AI assistant"
          :disabled="streaming"
          @keyup.enter="sendMessage"
        />
        <button class="btn btn-primary" @click="sendMessage" :disabled="streaming || !userInput.trim()">
          <i class="bi bi-send"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-chat-panel {
  border-left: 1px solid #dee2e6;
  background: #fff;
  min-height: 0;
}

.chat-header {
  border-bottom: 1px solid #eee;
  background: #fafbfc;
  flex-shrink: 0;
}

.context-banner {
  background: #e8f5e9;
  color: #2e7d32;
  font-size: 0.72rem;
  flex-shrink: 0;
  border-bottom: 1px solid #c8e6c9;
}

.context-banner-generic {
  background: #fff3e0;
  color: #e65100;
  border-bottom-color: #ffe0b2;
}
.context-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}
.context-pill {
  background: rgba(255,255,255,0.45);
  border: 1px solid rgba(46,125,50,0.25);
  border-radius: 20px;
  padding: 0.1rem 0.55rem;
  font-size: 0.68rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.chat-messages {
  overflow-y: auto;
  padding: 0.75rem;
  min-height: 0;
}

.empty-chat { opacity: 0.5; }

.chat-message {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  align-items: flex-start;
}

.chat-message.user { flex-direction: row-reverse; }

.message-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 0.8rem;
}

.chat-message.user .message-avatar { background: var(--bs-primary); color: white; }
.chat-message.assistant .message-avatar { background: #e9ecef; color: #495057; }

.message-bubble {
  max-width: 80%;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  font-size: 0.82rem;
  line-height: 1.5;
  word-break: break-word;
}

.chat-message.user .message-bubble {
  background: var(--bs-primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.chat-message.assistant .message-bubble {
  background: #f0f2f5;
  color: #212529;
  border-bottom-left-radius: 4px;
}

.message-bubble :deep(code) {
  font-size: 0.75rem;
  background: rgba(0, 0, 0, 0.06);
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
}

.message-bubble :deep(.code-block-wrapper) {
  position: relative;
  margin: 0.5rem 0;
  border-radius: 6px;
  overflow: hidden;
}
.message-bubble :deep(.code-block-actions) {
  display: flex;
  gap: 0.3rem;
  justify-content: flex-end;
  background: #2d2d2d;
  padding: 0.3rem 0.4rem;
  border-bottom: 1px solid #3a3a3a;
}
.message-bubble :deep(.copy-code-btn),
.message-bubble :deep(.replace-code-btn) {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: #d4d4d4;
  font-size: 0.65rem;
  padding: 0.15rem 0.55rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
}
.message-bubble :deep(.copy-code-btn:hover) {
  background: rgba(255,255,255,0.18);
}
.message-bubble :deep(.replace-code-btn) {
  color: #7dd3a8;
  border-color: rgba(125,211,168,0.3);
}
.message-bubble :deep(.replace-code-btn:hover) {
  background: rgba(125,211,168,0.15);
}
.message-bubble :deep(pre) {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 0.6rem 0.5rem;
  border-radius: 0;
  font-size: 0.72rem;
  overflow-x: auto;
  margin: 0;
  white-space: pre-wrap;
}

.chat-input {
  border-top: 1px solid #eee;
  background: #fafbfc;
  flex-shrink: 0;
}

.typing-indicator { display: inline-flex; gap: 3px; padding: 0.25rem 0; }
.typing-indicator span {
  width: 6px; height: 6px; border-radius: 50%; background: #adb5bd;
  animation: typing 1.2s infinite ease-in-out;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}
</style>
