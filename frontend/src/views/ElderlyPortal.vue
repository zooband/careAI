<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col bg-warm-50">
    <!-- Nav -->
    <nav class="flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-primary-100 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link to="/" class="font-bold text-primary-700 flex items-center gap-1.5 text-base">
          <i class="fas fa-heart text-primary-500"></i> 亲伴 AI
        </router-link>
        <span class="text-sm px-3 py-1 bg-accent/10 text-accent-dark rounded-full font-medium">
          <i class="fas fa-tv mr-1"></i>老人终端
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500">{{ currentElderly.avatar }} {{ currentElderly.name }}</span>
        <div class="flex items-center gap-1.5 text-sm text-gray-400">
          <span class="w-2 h-2 rounded-full" :class="connected?'bg-green-400':'bg-red-400'"></span>
          {{ connected ? '在线' : '重连中...' }}
        </div>
        <button @click="handleLogout" class="text-sm text-gray-400 hover:text-red-500 transition-colors">
          <i class="fas fa-sign-out-alt mr-1"></i>退出
        </button>
      </div>
    </nav>

    <!-- New push notification -->
    <transition name="slide">
      <div v-if="incomingTask"
        class="flex-shrink-0 mx-6 mt-2 px-5 py-4 bg-gradient-to-r from-primary-600 to-primary-500 rounded-2xl shadow-lg
               flex items-center gap-4 text-white cursor-pointer"
        @click="playIncoming">
        <i class="fas fa-bell text-2xl animate-pulse"></i>
        <div class="flex-1">
          <p class="text-lg font-bold">新的照护消息！点击播放</p>
          <p class="text-sm text-white/80 truncate">{{ incomingTask.rewritten || incomingTask.content }}</p>
        </div>
        <button @click.stop="dismissIncoming" class="text-white/60 hover:text-white text-xl">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </transition>

    <!-- Content -->
    <div class="flex-1 flex flex-col px-6 pb-4 overflow-hidden min-h-0 pt-4">
      <!-- Welcome -->
      <div class="flex-shrink-0 flex items-center gap-3 mb-4">
        <span class="text-3xl">{{ currentElderly.avatar }}</span>
        <span class="text-xl font-bold text-gray-800">{{ currentElderly.name }}，欢迎回来</span>
        <span class="text-sm text-gray-400 ml-auto">
          <i class="fas fa-check-circle text-green-500 mr-1"></i>今日 {{ history.length }} 条已读
        </span>
      </div>

      <!-- Recommended Videos -->
      <div class="flex-shrink-0 flex items-center gap-2 mb-3">
        <span class="text-base font-bold text-gray-600"><i class="fas fa-video mr-1.5"></i>推荐视频</span>
      </div>
      <div class="flex-shrink-0 overflow-x-auto pb-3 -mx-6 px-6">
        <div class="flex gap-4" style="min-width:max-content">
          <button v-for="video in recommended" :key="video.id"
            @click="playVideo(video.video_url, video.title)"
            class="flex-shrink-0 w-56 bg-white/70 backdrop-blur-sm rounded-2xl border border-white/50 shadow-sm overflow-hidden
                   group hover:shadow-lg hover:border-primary-200 transition-all text-left">
            <div class="relative h-28 bg-gray-800/10 overflow-hidden">
              <video :src="video.video_url" class="w-full h-full object-cover opacity-60 group-hover:opacity-90 transition-opacity" muted preload="metadata"></video>
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-12 h-12 bg-white/90 rounded-full flex items-center justify-center shadow group-hover:scale-110 transition-transform">
                  <i class="fas fa-play text-lg text-primary-600 ml-0.5"></i>
                </div>
              </div>
            </div>
            <div class="px-4 py-3">
              <p class="font-bold text-gray-800 truncate">{{ video.title }}</p>
              <p class="text-sm text-gray-400 mt-0.5">{{ video.duration }}s</p>
            </div>
          </button>
        </div>
      </div>

      <!-- History -->
      <div class="flex-shrink-0 flex items-center gap-2 mb-3 mt-1">
        <span class="text-base font-bold text-gray-600"><i class="fas fa-clock-rotate mr-1.5"></i>历史记录</span>
      </div>
      <div class="flex-1 overflow-y-auto min-h-0">
        <div v-if="history.length === 0" class="text-center text-gray-400 text-base pt-8">
          <i class="fas fa-inbox mr-2"></i>暂无播放记录
        </div>
        <div v-for="(item,i) in history" :key="i"
          class="flex items-center gap-4 px-4 py-3 mb-2 bg-white/50 rounded-xl border border-gray-100/50">
          <span class="flex-shrink-0 w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
            <i class="fas fa-play text-primary-600"></i>
          </span>
          <div class="flex-1 min-w-0">
            <p class="font-medium text-gray-700 truncate">{{ item.title || item.rewritten }}</p>
            <p class="text-sm text-gray-400">{{ formatTime(item.played_at || item.pushed_at) }}</p>
          </div>
          <button @click="playVideo(item.video_url, item.title)"
            class="text-sm text-primary-600 hover:text-primary-800 flex-shrink-0 font-medium">
            <i class="fas fa-rotate-right mr-1"></i>再看一次
          </button>
        </div>
      </div>
    </div>
    <div class="flex-shrink-0 text-center pb-3 text-sm text-gray-400">AI 亲情陪伴助手 · 由家人授权创建</div>

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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAuth, logout } from '../auth'

const router = useRouter()
const auth = getAuth()
const recommended = ref([])
const history = ref([])
const currentElderly = ref({ name: auth?.user?.name||'王奶奶', avatar: auth?.user?.avatar||'👵' })
const connected = ref(true)
const incomingTask = ref(null)
const elderlyId = auth?.user?.id || 1
const listening = ref(false)
const speechResult = ref(null)
let pollTimer = null

const demoVideos = [
  { id:1, title:'💊 按时吃药', video_url:'/api/videos/medication_reminder.mp4', duration:15 },
  { id:2, title:'🏃 康复运动', video_url:'/api/videos/exercise_reminder.mp4', duration:12 },
  { id:3, title:'🍚 晚饭时间', video_url:'/api/videos/dinner_reminder.mp4', duration:10 },
  { id:4, title:'🌙 早点休息', video_url:'/api/videos/bedtime_reminder.mp4', duration:12 },
  { id:5, title:'💕 暖心问候', video_url:'/api/videos/daily_greeting.mp4', duration:12 },
  { id:6, title:'🤗 情绪安抚', video_url:'/api/videos/emotional_comfort.mp4', duration:15 },
]

function handleLogout() { logout(); router.push('/') }

function startPolling() { pollTimer = setInterval(pollPending, 3000); pollPending() }
function stopPolling() { if (pollTimer) clearInterval(pollTimer) }

async function pollPending() {
  try {
    const res = await fetch(`/api/tasks/pending?elderly_id=${elderlyId}`)
    const data = await res.json()
    connected.value = true
    if (data.pending?.length) {
      const task = data.pending[0]
      incomingTask.value = task
      setTimeout(() => { if (incomingTask.value === task) playIncoming() }, 1500)
    }
  } catch (_) { connected.value = false }
}

async function playIncoming() {
  const task = incomingTask.value; if (!task) return
  incomingTask.value = null
  try { await fetch('/api/tasks/ack', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({task_id:task.id}) }) } catch(_) {}
  history.value.unshift({ ...task, played_at: new Date().toISOString() })
  router.push({ name:'elderly-player', query:{ url: task.video_url, title: task.rewritten || task.content, duration:'15', mode: task.video_mode || 'interactive' } })
}
function dismissIncoming() { incomingTask.value = null }
function playVideo(url, title, videoMode) {
  router.push({ name:'elderly-player', query:{ url, title:title||'视频消息', duration:'15', mode: videoMode || 'prerecorded' } })
}
async function loadHistory() {
  try { const res=await fetch('/api/tasks/history'); const d=await res.json(); if(d.history) history.value=d.history.reverse() } catch(_) {}
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

onMounted(async () => { recommended.value=demoVideos; await loadHistory(); startPolling() })
onUnmounted(() => stopPolling())
</script>

<style scoped>
.slide-enter-active,.slide-leave-active{transition:all .4s ease}
.slide-enter-from{transform:translateY(-120%);opacity:0}
.slide-leave-to{transform:translateY(-120%);opacity:0}
.fade-enter-active,.fade-leave-active{transition:opacity .25s ease}
.fade-enter-from,.fade-leave-to{opacity:0}
</style>
