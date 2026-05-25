<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col bg-gray-50">
    <!-- Nav -->
    <nav class="flex-shrink-0 bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link to="/" class="font-bold text-primary-700 flex items-center gap-1.5 text-base">
          <i class="fas fa-heart text-primary-500"></i> 亲伴 AI
        </router-link>
        <span class="text-sm px-3 py-1 bg-gray-100 text-gray-600 rounded-full font-medium">
          <i class="fas fa-shield-alt mr-1"></i>管理后台
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500" v-if="auth"><i class="fas fa-user mr-1"></i>{{ auth?.user?.name }}</span>
        <button @click="handleLogout" class="text-sm text-gray-400 hover:text-red-500">
          <i class="fas fa-sign-out-alt mr-1"></i>{{ auth ? '退出' : '返回首页' }}
        </button>
      </div>
    </nav>

    <!-- Login form (if not authenticated) -->
    <div v-if="!auth" class="flex-1 flex items-center justify-center">
      <div class="bg-white rounded-2xl shadow-lg border p-8 w-96">
        <h2 class="text-xl font-bold text-gray-800 mb-5"><i class="fas fa-shield-alt mr-2"></i>管理员登录</h2>
        <div v-if="loginError" class="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm"><i class="fas fa-exclamation-circle mr-1"></i>{{ loginError }}</div>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">用户名</label>
            <input v-model="username" placeholder="管理员用户名"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">密码</label>
            <input v-model="password" type="password" placeholder="密码"
              @keydown.enter="adminLogin"
              class="w-full px-4 py-3 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div class="text-xs text-gray-400">演示账号: 管理员 / admin123</div>
          <button @click="adminLogin" :disabled="logging"
            class="w-full bg-gray-800 text-white rounded-xl py-3 font-medium hover:bg-gray-700 transition-colors">
            <i v-if="logging" class="fas fa-spinner fa-spin mr-1"></i>{{ logging ? '登录中...' : '登录' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Admin Dashboard -->
    <div v-else class="flex-1 flex flex-col px-6 py-4 overflow-hidden min-h-0">
      <!-- Stats -->
      <div class="flex-shrink-0 flex gap-4 mb-4">
        <div class="bg-white rounded-xl border px-5 py-3 flex items-center gap-3">
          <i class="fas fa-users text-primary-500 text-xl"></i>
          <div><div class="text-2xl font-bold text-gray-800">{{ users.length }}</div><div class="text-xs text-gray-400">总用户</div></div>
        </div>
        <div class="bg-white rounded-xl border px-5 py-3 flex items-center gap-3">
          <i class="fas fa-wrench text-blue-500 text-xl"></i>
          <div><div class="text-2xl font-bold text-gray-800">{{ users.filter(u=>u.role==='caregiver').length }}</div><div class="text-xs text-gray-400">护工</div></div>
        </div>
        <div class="bg-white rounded-xl border px-5 py-3 flex items-center gap-3">
          <i class="fas fa-user-plus text-accent text-xl"></i>
          <div><div class="text-2xl font-bold text-gray-800">{{ users.filter(u=>u.role==='elderly').length }}</div><div class="text-xs text-gray-400">老人</div></div>
        </div>
        <div class="flex-1"></div>
        <button @click="showAddModal=true" class="bg-primary-600 text-white rounded-xl px-5 py-2 text-sm font-medium hover:bg-primary-700 flex items-center gap-2">
          <i class="fas fa-plus"></i>添加用户
        </button>
      </div>

      <!-- User table -->
      <div class="flex-1 bg-white rounded-2xl border shadow-sm overflow-hidden flex flex-col min-h-0">
        <div class="overflow-x-auto flex-1">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b text-left">
              <tr>
                <th class="px-4 py-3 text-gray-500 font-medium">ID</th>
                <th class="px-4 py-3 text-gray-500 font-medium">头像</th>
                <th class="px-4 py-3 text-gray-500 font-medium">姓名</th>
                <th class="px-4 py-3 text-gray-500 font-medium">角色</th>
                <th class="px-4 py-3 text-gray-500 font-medium">年龄</th>
                <th class="px-4 py-3 text-gray-500 font-medium">状况/标签</th>
                <th class="px-4 py-3 text-gray-500 font-medium">创建时间</th>
                <th class="px-4 py-3 text-gray-500 font-medium">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in users" :key="u.id" class="border-b border-gray-100 hover:bg-gray-50">
                <td class="px-4 py-3 text-gray-500">{{ u.id }}</td>
                <td class="px-4 py-3 text-xl">{{ u.avatar }}</td>
                <td class="px-4 py-3 font-medium text-gray-800">{{ u.name }}</td>
                <td class="px-4 py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-medium"
                    :class="roleClass(u.role)">{{ roleLabel(u.role) }}</span>
                </td>
                <td class="px-4 py-3 text-gray-600">{{ u.age }}</td>
                <td class="px-4 py-3 text-gray-500 max-w-[200px] truncate">{{ u.condition || (u.traits||[]).join(', ') || '-' }}</td>
                <td class="px-4 py-3 text-gray-400 text-xs">{{ u.created_at?.slice(0,10) }}</td>
                <td class="px-4 py-3">
                  <button @click="editUser(u)" class="text-primary-500 hover:text-primary-700 mr-3"><i class="fas fa-edit"></i></button>
                  <button @click="deleteUser(u.id)" class="text-red-400 hover:text-red-600" :disabled="u.id===auth?.user?.id"><i class="fas fa-trash-can"></i></button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal||showEditModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" @click.self="closeModal">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-[480px] max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-5">
          <h3 class="text-lg font-bold text-gray-800">
            <i :class="showEditModal?'fas fa-edit':'fas fa-plus'" class="mr-2"></i>
            {{ showEditModal ? '编辑用户' : '添加用户' }}
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
        </div>

        <div v-if="formError" class="mb-4 p-3 bg-red-50 text-red-600 rounded-xl text-sm"><i class="fas fa-exclamation-circle mr-1"></i>{{ formError }}</div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">姓名</label>
            <input v-model="form.name" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">密码 (留空不修改)</label>
            <input v-model="form.password" type="password" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" :placeholder="showEditModal?'不修改则留空':'默认 123456'" />
          </div>
          <div class="flex gap-4">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-600 mb-1">角色</label>
              <select v-model="form.role" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400 bg-white">
                <option value="caregiver">护工</option>
                <option value="elderly">老人</option>
                <option value="admin">管理员</option>
              </select>
            </div>
            <div class="w-24">
              <label class="block text-sm font-medium text-gray-600 mb-1">年龄</label>
              <input v-model.number="form.age" type="number" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">头像 (emoji)</label>
            <input v-model="form.avatar" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div v-if="form.role==='elderly'">
            <label class="block text-sm font-medium text-gray-600 mb-1">健康状况</label>
            <input v-model="form.condition" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">标签 (逗号分隔)</label>
            <input v-model="form.traitsInput" placeholder="例如: 健忘, 温和, 喜欢听戏曲"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button @click="submitForm" :disabled="submitting"
            class="flex-1 bg-primary-600 text-white rounded-xl py-3 font-medium hover:bg-primary-700 transition-colors">
            <i v-if="submitting" class="fas fa-spinner fa-spin mr-1"></i>
            {{ showEditModal ? '保存修改' : '创建用户' }}
          </button>
          <button @click="closeModal" class="px-6 py-3 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAuth, login as authLogin, logout as authLogout } from '../auth'

const router = useRouter()
const auth = ref(getAuth())
const users = ref([])
const logging = ref(false)
const loginError = ref('')
const username = ref('')
const password = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingId = ref(null)
const submitting = ref(false)
const formError = ref('')

const form = ref({ name:'', password:'', role:'elderly', age:70, avatar:'👤', condition:'', traitsInput:'' })

function roleClass(r) {
  return { admin:'bg-purple-100 text-purple-700', caregiver:'bg-blue-100 text-blue-700', elderly:'bg-accent/10 text-accent-dark' }[r]||'bg-gray-100 text-gray-600'
}
function roleLabel(r) { return { admin:'管理员', caregiver:'护工', elderly:'老人' }[r]||r }

async function adminLogin() {
  if (!username.value.trim()) return
  logging.value = true; loginError.value = ''
  try {
    const res = await fetch('/api/auth/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:username.value, password:password.value, role:'admin'}) })
    const data = await res.json()
    if (!res.ok) { loginError.value = data.detail||'登录失败'; return }
    authLogin('admin', data.user)
    auth.value = getAuth()
    loadUsers()
  } catch(e) { loginError.value = '网络错误'
  } finally { logging.value = false }
}

function handleLogout() { authLogout(); auth.value = null; router.push('/') }

async function loadUsers() {
  try { const res=await fetch('/api/admin/users'); const d=await res.json(); users.value=d.users } catch(_) {}
}

function editUser(u) {
  editingId.value = u.id
  form.value = { name:u.name, password:'', role:u.role, age:u.age, avatar:u.avatar, condition:u.condition||'', traitsInput:(u.traits||[]).join(', ') }
  showEditModal.value = true
}

function closeModal() { showAddModal.value=false; showEditModal.value=false; editingId.value=null; formError.value='' }

async function submitForm() {
  if (!form.value.name.trim()) { formError.value = '请输入姓名'; return }
  submitting.value = true; formError.value = ''

  const payload = {
    name: form.value.name,
    password: form.value.password || '123456',
    role: form.value.role,
    avatar: form.value.avatar || '👤',
    age: form.value.age || 70,
    condition: form.value.condition || '',
    traits: form.value.traitsInput ? form.value.traitsInput.split(',').map(s=>s.trim()).filter(Boolean) : [],
  }

  try {
    let res
    if (showEditModal.value) {
      res = await fetch(`/api/admin/users/${editingId.value}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) })
    } else {
      res = await fetch('/api/admin/users', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) })
    }
    const d = await res.json()
    if (!res.ok) { formError.value = d.detail||'操作失败'; return }
    closeModal()
    loadUsers()
  } catch(e) { formError.value = '网络错误'
  } finally { submitting.value = false }
}

async function deleteUser(id) {
  if (!confirm('确定删除此用户？')) return
  try { await fetch(`/api/admin/users/${id}`, { method:'DELETE' }); loadUsers() } catch(_) {}
}

onMounted(async () => { if (auth.value) await loadUsers() })
</script>
