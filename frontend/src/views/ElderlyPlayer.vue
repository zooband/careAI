<template>
  <div class="fixed inset-0 bg-black z-50 flex flex-col">
    <!-- Top overlay -->
    <div class="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/60 to-transparent px-6 pt-6 pb-12">
      <div class="flex items-center justify-between">
        <button @click="goBack" class="text-white/80 hover:text-white flex items-center gap-2 text-lg transition-colors">
          <i class="fas fa-arrow-left text-xl"></i>
          <span v-if="!isPlaying" class="text-sm">返回</span>
        </button>
        <div v-if="!isPlaying" class="flex items-center gap-2">
          <span class="text-white/60 text-xs px-3 py-1 bg-white/10 rounded-full">
            AI 亲情陪伴助手 · 由家人授权创建
          </span>
          <span v-if="videoMode==='preview'" class="text-xs px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full">
            <i class="fas fa-video mr-1"></i>预制视频
          </span>
          <span v-else-if="videoMode==='digital'" class="text-xs px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full">
            <i class="fas fa-robot mr-1"></i>数字人视频
          </span>
          <span v-else class="text-xs px-3 py-1 bg-amber-500/20 text-amber-300 rounded-full">
            <i class="fas fa-microphone mr-1"></i>可交互视频
          </span>
        </div>
      </div>
    </div>

    <!-- Video container -->
    <div class="flex-1 flex items-center justify-center relative">
      <video
        ref="videoRef"
        :src="videoUrl"
        class="w-full h-full object-contain"
        @ended="onEnded"
        @error="onVideoError"
        @play="isPlaying = true"
        @pause="isPlaying = false"
        playsinline
        autoplay
      ></video>

      <!-- Center play button (when paused) -->
      <button
        v-if="!isPlaying && !hasEnded && !interrupted"
        @click="play"
        class="absolute inset-0 flex items-center justify-center bg-black/20 group cursor-pointer"
      >
        <div class="w-24 h-24 bg-white/90 rounded-full flex items-center justify-center shadow-2xl group-hover:scale-110 transition-transform">
          <i class="fas fa-play text-4xl text-primary-600 ml-1"></i>
        </div>
      </button>

      <!-- Lunch scenario reply input -->
      <div
        v-if="lunchAwaitingReply"
        class="absolute inset-0 bg-black/75 flex flex-col items-center justify-center gap-5 p-6"
      >
        <div class="w-full max-w-xl bg-white/95 rounded-2xl p-6 shadow-2xl">
          <div class="flex items-center gap-3 mb-4">
            <span class="w-10 h-10 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center">
              <i class="fas fa-comment-dots"></i>
            </span>
            <div>
              <p class="text-gray-900 text-lg font-bold">请输入奶奶的回复</p>
              <p class="text-gray-500 text-sm">系统会判断午饭反馈，并播放对应的下一段视频</p>
            </div>
          </div>
          <textarea
            v-model="lunchReply"
            rows="3"
            class="w-full rounded-xl border border-gray-200 p-4 text-base outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
            placeholder="例如：太咸了 / 很好吃，有我爱吃的清蒸鱼 / 都不爱吃，没胃口"
          ></textarea>
          <div v-if="lunchError" class="mt-3 text-sm text-red-600">{{ lunchError }}</div>
          <div class="mt-5 flex justify-end gap-3">
            <button @click="goBack" class="px-5 py-3 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50">
              返回
            </button>
            <button
              @click="submitLunchReply"
              :disabled="lunchSubmitting || !lunchReply.trim()"
              class="px-6 py-3 rounded-xl bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i v-if="lunchSubmitting" class="fas fa-spinner fa-spin mr-2"></i>
              确认并播放
            </button>
          </div>
        </div>
      </div>

      <!-- Ended overlay -->
      <div
        v-if="hasEnded"
        class="absolute inset-0 bg-black/70 flex flex-col items-center justify-center gap-6"
      >
        <i class="fas fa-check-circle text-6xl text-green-400"></i>
        <p class="text-white text-2xl font-bold">播放完成</p>
        <p class="text-white/60 text-lg">消息已送达，请查收~</p>
        <div class="flex gap-4 mt-4">
          <button @click="replay" class="btn-primary text-lg px-8 py-4 flex items-center gap-2">
            <i class="fas fa-rotate-right"></i> 再看一次
          </button>
          <button @click="goBack" class="btn-outline !border-white/30 !text-white text-lg px-8 py-4 flex items-center gap-2">
            <i class="fas fa-arrow-left"></i> 返回列表
          </button>
        </div>
      </div>

      <!-- Placeholder when demo video assets are not uploaded yet -->
      <div
        v-if="videoError"
        class="absolute inset-0 bg-black/80 flex flex-col items-center justify-center gap-5 p-6"
      >
        <i class="fas fa-film text-6xl text-white/70"></i>
        <p class="text-white text-2xl font-bold">视频素材待上传</p>
        <p class="text-white/60 text-center max-w-lg">{{ videoUrl }}</p>
        <p v-if="lunchResult?.reply_text" class="text-blue-200 text-center max-w-xl">{{ lunchResult.reply_text }}</p>
        <div class="flex gap-3">
          <button v-if="isLunchScenario && !lunchBranchPlayed" @click="showLunchReplyInput"
            class="px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700">
            输入老人回复
          </button>
          <button @click="goBack" class="px-6 py-3 bg-white/20 text-white rounded-xl font-medium hover:bg-white/30">
            返回
          </button>
        </div>
      </div>

      <!-- Interrupt overlay (dangerous content detected) -->
      <div
        v-if="interrupted"
        class="absolute inset-0 bg-red-900/90 flex flex-col items-center justify-center gap-4 p-8"
      >
        <div class="w-20 h-20 bg-red-500/30 rounded-full flex items-center justify-center">
          <i class="fas fa-hand text-5xl text-white"></i>
        </div>
        <p class="text-white text-2xl font-bold">检测到不适当内容</p>
        <p class="text-white/70 text-lg text-center max-w-md">{{ interruptReason }}</p>
        <ul v-if="interruptIssues.length" class="text-red-200 text-sm space-y-1">
          <li v-for="(issue,i) in interruptIssues" :key="i">· {{ issue }}</li>
        </ul>
        <div class="flex gap-4 mt-4">
          <button @click="goBack" class="px-8 py-3 bg-white/20 text-white rounded-xl font-medium hover:bg-white/30 transition-colors">
            <i class="fas fa-arrow-left mr-1"></i>返回
          </button>
          <button @click="replay" class="px-8 py-3 bg-white text-red-600 rounded-xl font-medium hover:bg-gray-100 transition-colors">
            <i class="fas fa-rotate-right mr-1"></i>重播
          </button>
        </div>
      </div>

      <!-- Speech transcript overlay (safe interaction) -->
      <transition name="fade">
        <div v-if="transcript"
          class="absolute bottom-24 left-1/2 -translate-x-1/2 bg-black/70 backdrop-blur-sm rounded-2xl px-6 py-4 max-w-lg w-[90%] text-center">
          <p class="text-white/60 text-sm mb-1"><i class="fas fa-microphone mr-1"></i>你说：</p>
          <p class="text-white text-lg">{{ transcript.text }}</p>
          <div class="mt-2 pt-2 border-t border-white/20">
            <p class="text-primary-300 text-sm"><i class="fas fa-heart mr-1"></i>{{ transcript.rewritten_text }}</p>
          </div>
        </div>
      </transition>
    </div>

    <!-- Bottom signature + Mic -->
    <div class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent px-6 pt-12 pb-6">
      <div class="flex items-end justify-between">
        <div class="text-center flex-1">
          <p class="text-white/50 text-sm">AI 亲情陪伴助手 · 由家人授权创建</p>
        </div>
        <button v-if="videoMode === 'interactive'" @click="startListening" :disabled="hasEnded"
          class="w-14 h-14 rounded-full shadow-xl flex items-center justify-center transition-all flex-shrink-0"
          :class="listening ? 'bg-red-500 scale-110 animate-pulse' : 'bg-white/20 hover:bg-white/30'">
          <i class="fas fa-microphone text-xl" :class="listening ? 'text-white' : 'text-white/80'"></i>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="absolute inset-0 bg-black flex items-center justify-center">
      <div class="text-center">
        <div class="w-16 h-16 border-4 border-primary-400 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-white/70 text-lg">正在加载视频...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const videoRef = ref(null)
const videoUrl = ref('')
const isPlaying = ref(false)
const hasEnded = ref(false)
const loading = ref(true)
const listening = ref(false)
const videoMode = ref('preview')
const interrupted = ref(false)
const interruptReason = ref('')
const interruptIssues = ref([])
const transcript = ref(null)
const scenarioId = ref('')
const taskId = ref(null)
const elderlyId = ref(null)
const lunchAwaitingReply = ref(false)
const lunchReply = ref('')
const lunchSubmitting = ref(false)
const lunchError = ref('')
const lunchResult = ref(null)
const lunchBranchPlayed = ref(false)
const videoError = ref(false)
const isLunchScenario = ref(false)

onMounted(() => {
  videoUrl.value = route.query.url || '/api/videos/medication_reminder.mp4'
  videoMode.value = route.query.mode || 'preview'
  scenarioId.value = route.query.scenario || ''
  taskId.value = route.query.task_id || null
  elderlyId.value = route.query.elderly_id || null
  isLunchScenario.value = scenarioId.value === 'lunch_checkin' || route.query.requires_reply === '1'

  setTimeout(() => {
    loading.value = false
    if (videoRef.value) {
      videoRef.value.play().catch(() => {
        isPlaying.value = false
      })
    }
  }, 500)
})

function play() {
  if (videoRef.value) {
    hasEnded.value = false
    interrupted.value = false
    transcript.value = null
    videoError.value = false
    videoRef.value.play()
  }
}

function replay() {
  hasEnded.value = false
  interrupted.value = false
  transcript.value = null
  videoError.value = false
  lunchAwaitingReply.value = false
  if (videoRef.value) {
    videoRef.value.currentTime = 0
    videoRef.value.play()
  }
}

function onEnded() {
  isPlaying.value = false
  if (isLunchScenario.value && !lunchBranchPlayed.value) {
    showLunchReplyInput()
    return
  }
  hasEnded.value = true
}

function onVideoError() {
  loading.value = false
  isPlaying.value = false
  videoError.value = true
}

function showLunchReplyInput() {
  hasEnded.value = false
  interrupted.value = false
  videoError.value = false
  lunchAwaitingReply.value = true
}

async function submitLunchReply() {
  if (!lunchReply.value.trim() || lunchSubmitting.value) return
  lunchSubmitting.value = true
  lunchError.value = ''
  try {
    const res = await fetch('/api/scenarios/lunch/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        reply: lunchReply.value,
        task_id: taskId.value ? Number(taskId.value) : null,
        elderly_id: elderlyId.value ? Number(elderlyId.value) : null,
      }),
    })
    const data = await res.json()
    if (!res.ok || !data.success) {
      throw new Error(data.detail || '分析失败，请重试')
    }
    lunchResult.value = data
    lunchAwaitingReply.value = false
    lunchBranchPlayed.value = true
    hasEnded.value = false
    videoError.value = false
    videoUrl.value = data.video_url
    transcript.value = { text: lunchReply.value, rewritten_text: data.reply_text }
    setTimeout(() => {
      if (videoRef.value) {
        videoRef.value.load()
        videoRef.value.play().catch(() => { isPlaying.value = false })
      }
    }, 100)
  } catch (e) {
    lunchError.value = e.message || '网络错误，请重试'
  } finally {
    lunchSubmitting.value = false
  }
}

function goBack() {
  router.push('/elderly')
}

async function startListening() {
  if (listening.value || hasEnded.value) return
  listening.value = true; transcript.value = null; interrupted.value = false

  // Simulate recording
  await new Promise(r => setTimeout(r, 2000))

  try {
    const blob = new Blob(['mock audio'], { type:'audio/wav' })
    const form = new FormData()
    form.append('file', blob, 'speech.wav')
    const res = await fetch('/api/audio/transcribe', { method:'POST', body: form })
    const data = await res.json()

    if (!data.safe) {
      // Interrupt! Stop video, show warning
      if (videoRef.value) { videoRef.value.pause(); videoRef.value.currentTime = 0 }
      isPlaying.value = false
      interrupted.value = true
      interruptReason.value = data.text
      interruptIssues.value = data.issues || []
    } else {
      // Show caring response overlay, auto-dismiss after 5s
      transcript.value = data
      setTimeout(() => { if (transcript.value === data) transcript.value = null }, 5000)
    }
  } catch (_) {
    transcript.value = { text:'网络错误', rewritten_text:'请检查网络连接后重试~' }
    setTimeout(() => { transcript.value = null }, 3000)
  } finally { listening.value = false }
}
</script>

<style scoped>
.fade-enter-active,.fade-leave-active{transition:opacity .3s ease}
.fade-enter-from,.fade-leave-to{opacity:0}
</style>
