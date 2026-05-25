<template>
  <div class="h-screen w-screen overflow-hidden gradient-bg flex flex-col">
    <div class="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-400 via-accent to-primary-500"></div>
    <div class="flex-1 flex items-center justify-center px-6">
      <div class="w-full max-w-md">
        <!-- Brand -->
        <div class="text-center mb-10">
          <div class="text-5xl mb-3"><i class="fas fa-heart text-primary-500"></i></div>
          <h1 class="text-3xl font-black text-gray-900">亲伴 AI</h1>
          <p class="text-base text-gray-500 mt-2">亲情数字陪伴助手</p>
        </div>

        <!-- Login Card -->
        <div class="bg-white/80 backdrop-blur-sm rounded-3xl border border-white/50 shadow-xl p-8">
          <!-- Tabs -->
          <div class="flex bg-gray-100 rounded-2xl p-1 mb-6">
            <button @click="tab='caregiver'"
              class="flex-1 py-3 rounded-xl text-base font-medium transition-all"
              :class="tab==='caregiver'?'bg-white shadow text-primary-700':'text-gray-500 hover:text-gray-700'">
              <i class="fas fa-wrench mr-1.5"></i>护工登录
            </button>
            <button @click="tab='elderly'"
              class="flex-1 py-3 rounded-xl text-base font-medium transition-all"
              :class="tab==='elderly'?'bg-white shadow text-accent-dark':'text-gray-500 hover:text-gray-700'">
              <i class="fas fa-tv mr-1.5"></i>老人登录
            </button>
          </div>

          <!-- Loading / Error -->
          <div v-if="loginError" class="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm flex items-center gap-2">
            <i class="fas fa-exclamation-circle"></i>{{ loginError }}
          </div>

          <!-- Login Form -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1.5">
                <i class="fas fa-user mr-1"></i>用户名
              </label>
              <input v-model="username" placeholder="请输入用户名"
                class="w-full px-5 py-3.5 rounded-2xl border border-gray-200 bg-warm-50 text-base outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 placeholder-gray-300 transition-all" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-600 mb-1.5">
                <i class="fas fa-lock mr-1"></i>密码
              </label>
              <input v-model="password" type="password" placeholder="请输入密码"
                @keydown.enter="handleLogin"
                class="w-full px-5 py-3.5 rounded-2xl border border-gray-200 bg-warm-50 text-base outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 placeholder-gray-300 transition-all" />
            </div>

            <div class="text-xs text-gray-400">
              <template v-if="tab==='caregiver'">演示账号: 张三 / 123456</template>
              <template v-else>演示账号: 王奶奶 / 123456</template>
            </div>

            <button @click="handleLogin" :disabled="!username.trim()||logging"
              class="w-full btn-primary text-base py-3.5 flex items-center justify-center gap-2"
              :class="tab==='elderly'?'!bg-accent hover:!bg-accent-dark':''">
              <i v-if="logging" class="fas fa-spinner fa-spin"></i>
              <i v-else :class="tab==='caregiver'?'fas fa-wrench':'fas fa-tv'"></i>
              {{ logging ? '登录中...' : '进入' }}
              <template v-if="tab==='caregiver'">护工工作台</template>
              <template v-else>老人终端</template>
            </button>

            <div class="text-center">
              <router-link to="/admin" class="text-xs text-gray-400 hover:text-primary-600 transition-colors">
                <i class="fas fa-shield-alt mr-1"></i>管理员登录
              </router-link>
            </div>
          </div>
        </div>
        <p class="text-center text-xs text-gray-400 mt-6">AI 亲情陪伴助手 · 由家人授权创建</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login as authLogin } from '../auth'

const router = useRouter()
const tab = ref('caregiver')
const username = ref('')
const password = ref('')
const logging = ref(false)
const loginError = ref('')

async function handleLogin() {
  if (!username.value.trim() || !password.value.trim()) return
  logging.value = true
  loginError.value = ''
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: username.value, password: password.value, role: tab.value }),
    })
    const data = await res.json()
    if (!res.ok) {
      loginError.value = data.detail || '登录失败'
      return
    }
    authLogin(tab.value, data.user)
    router.push(tab.value === 'caregiver' ? '/caregiver' : '/elderly')
  } catch (e) {
    loginError.value = '网络错误，请重试'
  } finally {
    logging.value = false
  }
}
</script>
