<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col bg-warm-50">
    <!-- Nav -->
    <nav class="flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-primary-100 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link to="/" class="font-bold text-primary-700 flex items-center gap-1.5 text-base">
          <i class="fas fa-heart text-primary-500"></i> 家有 AI 宝
        </router-link>
        <span class="text-sm px-3 py-1 bg-accent/10 text-accent-dark rounded-full font-medium">
          <i class="fas fa-tv mr-1"></i>老人终端
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500">{{ currentElderly.avatar }} {{ currentElderly.name }}</span>
        <button @click="handleLogout" class="text-sm text-gray-400 hover:text-red-500 transition-colors">
          <i class="fas fa-sign-out-alt mr-1"></i>退出
        </button>
      </div>
    </nav>

    <!-- Incoming task toasts (stacked top-right) -->
    <div class="fixed top-20 right-6 z-50 flex flex-col gap-2 max-w-sm">
      <div v-for="(toast, i) in pendingToasts" :key="toast.id"
        @click="playToast(toast)"
        class="bg-white rounded-2xl shadow-xl border border-primary-100 p-4 cursor-pointer hover:shadow-lg transition-shadow animate-[slideIn_0.3s_ease]">
        <div class="flex items-start gap-3">
          <span class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent flex items-center justify-center flex-shrink-0">
            <i class="fas fa-bell text-white text-sm"></i>
          </span>
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <p class="font-bold text-gray-800 text-sm">新的照护消息</p>
              <button @click.stop="dismissToast(toast.id)" class="text-gray-300 hover:text-gray-500 flex-shrink-0">
                <i class="fas fa-times"></i>
              </button>
            </div>
            <p class="text-sm text-gray-600 mt-1 line-clamp-2">{{ toast.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Content — WeChat-style message feed -->
    <div class="flex-1 flex flex-col px-6 pb-2 overflow-hidden min-h-0 pt-3">
      <!-- Welcome -->
      <div class="flex-shrink-0 flex items-center gap-3 mb-2">
        <span class="text-3xl">{{ currentElderly.avatar }}</span>
        <div class="flex-1 min-w-0">
          <span class="text-lg font-bold text-gray-800">{{ currentElderly.name }}</span>
          <span class="text-sm text-gray-400 ml-2">今日 {{ history.length }} 条消息</span>
        </div>
        <span class="w-2 h-2 rounded-full" :class="connected?'bg-green-400':'bg-red-400'"></span>
      </div>

      <!-- Message feed -->
      <div ref="feedRef" class="flex-1 overflow-y-auto min-h-0 space-y-3 py-2">
        <div v-if="history.length === 0" class="text-center text-gray-400 text-base pt-12">
          <i class="fas fa-inbox mr-2"></i>暂无消息
        </div>
        <div v-for="(item,i) in history" :key="i"
          @click="playHistoryItem(item)"
          class="flex gap-3 px-4 py-3 bg-white rounded-2xl border border-gray-100/80 shadow-sm cursor-pointer hover:bg-primary-50/50 transition-colors">
          <span class="flex-shrink-0 w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center mt-0.5">
            <i class="fas fa-play text-primary-600 text-sm ml-0.5"></i>
          </span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-800 leading-snug">{{ item.rewritten || item.title || item.content }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ formatTime(item.pushed_at || item.played_at) }}</p>
          </div>
        </div>
      </div>
    </div>
    <div class="flex-shrink-0 text-center pb-2 text-xs text-gray-400">AI 亲情陪伴助手 · 由家人授权创建</div>

    <!-- Floating Mic Button -->
    <button @click="startListening"
      class="fixed bottom-8 right-8 w-16 h-16 rounded-full shadow-xl flex items-center justify-center z-40 transition-all"
      :class="listening ? 'bg-red-500 scale-110 animate-pulse' : 'bg-primary-600 hover:bg-primary-700 hover:scale-105'">
      <i class="fas fa-microphone text-2xl text-white"></i>
    </button>

    <!-- Speech Result Modal -->
    <transition name="fade">
      <div v-if="speechResult" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-6" @click.self="speechResult=null">
        <div class="bg-white rounded-3xl shadow-2xl p-6 w-full max-w-md">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-bold text-gray-800 flex items-center gap-2">
              <i class="fas fa-comment-dots text-primary-500"></i>我听你说
            </h3>
            <button @click="speechResult=null" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
          </div>
          <div class="mb-4 p-4 bg-gray-50 rounded-2xl">
            <p class="text-sm text-gray-500 mb-1">你说：</p>
            <p class="text-lg text-gray-800">{{ speechResult.text }}</p>
          </div>
          <div v-if="speechResult.safe" class="p-4 bg-green-50 rounded-2xl border border-green-200">
            <p class="text-sm text-green-600 mb-1"><i class="fas fa-check-circle mr-1"></i>AI 回复</p>
            <p class="text-lg text-green-800">{{ speechResult.rewritten_text }}</p>
          </div>
          <div v-else class="p-4 bg-red-50 rounded-2xl border border-red-200">
            <p class="text-sm text-red-600 mb-1"><i class="fas fa-exclamation-triangle mr-1"></i>检测到敏感内容</p>
            <ul class="text-sm text-red-700 space-y-1">
              <li v-for="(issue,i) in speechResult.issues" :key="i">· {{ issue }}</li>
            </ul>
          </div>
          <button @click="speechResult=null" class="w-full mt-4 py-3 bg-gray-800 text-white rounded-xl font-medium hover:bg-gray-700">知道了</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getAuth, logout } from '../auth'

const router = useRouter()
const auth = getAuth()
const history = ref([])
const currentElderly = ref({ name: auth?.user?.name||'王奶奶', avatar: auth?.user?.avatar||'👵' })
const connected = ref(true)
const elderlyId = auth?.user?.id || 1
const listening = ref(false)
const speechResult = ref(null)
const feedRef = ref(null)
const SEEN_KEY = 'qinban_seen_ids'
const TOAST_KEY = 'qinban_pending_toasts'
const pendingToasts = ref(loadToasts())
let pollTimer = null
let seenTaskIds = new Set(loadSeenIds())
let toastIdCounter = pendingToasts.value.length + 1

function loadToasts() {
  try { return JSON.parse(sessionStorage.getItem(TOAST_KEY) || '[]') } catch { return [] }
}
function saveToasts() {
  sessionStorage.setItem(TOAST_KEY, JSON.stringify(pendingToasts.value))
}
function loadSeenIds() {
  try { return JSON.parse(sessionStorage.getItem(SEEN_KEY) || '[]') } catch { return [] }
}
function saveSeenIds() {
  sessionStorage.setItem(SEEN_KEY, JSON.stringify([...seenTaskIds]))
}
watch(pendingToasts, saveToasts, { deep: true })


function handleLogout() { sessionStorage.removeItem(TOAST_KEY); sessionStorage.removeItem(SEEN_KEY); logout(); router.push('/') }

function startPolling() { pollTimer = setInterval(pollPending, 3000); pollPending() }
function stopPolling() { if (pollTimer) clearInterval(pollTimer) }

async function pollPending() {
  try {
    const res = await fetch(`/api/tasks/pending?elderly_id=${elderlyId}`)
    const data = await res.json()
    connected.value = true
    if (data.pending?.length) {
      for (const task of data.pending) {
        if (seenTaskIds.has(task.id)) continue
        seenTaskIds.add(task.id)
        try {
          await fetch('/api/tasks/ack', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({task_id:task.id}) })
        } catch(_) {}
        const entry = { ...task, played_at: new Date().toISOString() }
        history.value.unshift(entry)
        const toastId = toastIdCounter++
        pendingToasts.value.unshift({ id: toastId, taskId: task.id, content: task.rewritten || task.content, video_url: task.video_url, mode: task.video_mode || 'interactive', title: task.rewritten || task.content, scenario_id: task.scenario_id || '', requires_reply: !!task.requires_reply })
      }
      saveSeenIds()
      nextTick(() => { if (feedRef.value) feedRef.value.scrollTop = 0 })
    }
  } catch (_) { connected.value = false }
}

function playToast(toast) {
  dismissToast(toast.id)
  router.push({ name:'elderly-player', query:{
    url: toast.video_url, title: toast.title || '视频消息', duration: '15',
    mode: toast.mode || 'interactive',
    scenario: toast.scenario_id || '',
    requires_reply: toast.requires_reply ? '1' : '',
  } })
}
function dismissToast(id) {
  pendingToasts.value = pendingToasts.value.filter(t => t.id !== id)
}

function playHistoryItem(item) {
  router.push({ name:'elderly-player', query:{
    url: item.video_url, title: item.title || item.rewritten || '视频消息', duration: '15',
    mode: item.mode || item.video_mode || 'prerecorded',
    scenario: item.scenario_id || '',
    requires_reply: item.requires_reply ? '1' : '',
  } })
}
async function loadHistory() {
  try {
    const res=await fetch('/api/tasks/history'); const d=await res.json()
    if(d.history) { history.value=d.history.reverse(); d.history.forEach(h => { if (h.task_id) seenTaskIds.add(h.task_id) }); saveSeenIds() }
  } catch(_) {}
}
function formatTime(iso) {
  if(!iso) return ''; const d=new Date(iso)
  return `今天 ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

async function startListening() {
  if (listening.value) return
  listening.value = true; speechResult.value = null
  // Simulate recording for 2s, then send to API
  await new Promise(r => setTimeout(r, 2000))
  try {
    const blob = new Blob(['mock audio data'], { type:'audio/wav' })
    const form = new FormData()
    form.append('file', blob, 'speech.wav')
    const res = await fetch('/api/audio/transcribe', { method:'POST', body: form })
    speechResult.value = await res.json()
  } catch (_) {
    speechResult.value = { text:'网络错误，请重试', safe:true, issues:[], rewritten_text:'请检查网络连接后再试~' }
  } finally { listening.value = false }
}

onMounted(async () => { await loadHistory(); startPolling() })
onUnmounted(() => stopPolling())
</script>

<style scoped>
.fade-enter-active,.fade-leave-active{transition:opacity .25s ease}
.fade-enter-from,.fade-leave-to{opacity:0}
@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}
</style>
