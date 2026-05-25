<template>
  <div class="h-screen w-screen overflow-hidden flex flex-col bg-warm-50">
    <!-- Nav -->
    <nav class="flex-shrink-0 bg-white/80 backdrop-blur-md border-b border-primary-100 px-6 py-3 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <router-link to="/" class="font-bold text-primary-700 flex items-center gap-1.5 text-base">
          <i class="fas fa-heart text-primary-500"></i> 亲伴 AI
        </router-link>
        <span class="text-sm px-3 py-1 bg-primary-100 text-primary-600 rounded-full font-medium">
          <i class="fas fa-wrench mr-1"></i>护工工作台
        </span>
      </div>
      <div class="flex items-center gap-4">
        <span class="text-sm text-gray-500"><i class="fas fa-user mr-1"></i>{{ auth?.user?.name || '护工' }}</span>
        <span class="w-2 h-2 rounded-full bg-green-400"></span>
        <span class="text-sm text-gray-400">在线</span>
        <button @click="handleLogout" class="text-sm text-gray-400 hover:text-red-500 transition-colors">
          <i class="fas fa-sign-out-alt mr-1"></i>退出
        </button>
      </div>
    </nav>

    <!-- Elderly Search + Cards Row -->
    <div class="flex-shrink-0 px-6 py-3">
      <div class="flex items-center gap-3 mb-3">
        <div class="flex-1 relative">
          <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"></i>
          <input v-model="searchQuery" @input="onSearchInput" placeholder="搜索老人（姓名/标签）..."
            class="w-full pl-10 pr-4 py-2.5 bg-white/70 border border-gray-200 rounded-xl text-base outline-none focus:border-primary-400" />
        </div>
        <button @click="showAddModal=true" class="bg-primary-600 text-white rounded-xl px-5 py-2.5 text-sm font-medium hover:bg-primary-700 flex items-center gap-2 flex-shrink-0">
          <i class="fas fa-plus"></i>添加老人
        </button>
      </div>
      <div class="overflow-x-auto">
        <div class="flex gap-4" style="min-width:max-content">
          <button v-for="elder in elderlyList" :key="elder.id"
            @click="selectElder(elder)"
            :class="['flex items-center gap-4 px-5 py-4 rounded-2xl border-2 transition-all flex-shrink-0',
              selected?.id === elder.id
                ? 'border-primary-500 bg-white shadow-lg shadow-primary-500/10'
                : 'border-transparent bg-white/70 hover:bg-white hover:shadow']">
            <span class="text-4xl">{{ elder.avatar }}</span>
            <div class="text-left min-w-0">
              <div class="font-bold text-gray-800">{{ elder.name }}</div>
              <div class="text-sm text-gray-500">{{ elder.age }}岁 · {{ elder.condition }}</div>
              <div class="flex gap-1.5 mt-1.5">
                <span v-for="t in (elder.traits||[]).slice(0,3)" :key="t"
                  class="px-2.5 py-1 bg-primary-50 text-primary-600 rounded text-xs font-medium">{{ t }}</span>
                <span v-if="(elder.traits||[]).length > 3" class="text-xs text-gray-400 self-center">+{{ (elder.traits||[]).length-3 }}</span>
              </div>
            </div>
          </button>
          <div v-if="elderlyList.length === 0" class="flex items-center px-6 py-4 text-gray-400 text-base">
            <i class="fas fa-inbox mr-2"></i>{{ searchQuery ? '没有匹配的老人' : '暂无老人用户' }}
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div v-if="selected" class="flex-1 flex gap-5 px-6 pb-5 overflow-hidden min-h-0">
      <!-- Left: Profile Panel -->
      <div class="w-[400px] bg-white/70 backdrop-blur-sm rounded-2xl border border-white/50 shadow p-5 flex flex-col overflow-hidden flex-shrink-0">
        <div class="flex-shrink-0 flex items-start gap-4 mb-3">
          <div class="relative flex-shrink-0">
            <div class="w-16 h-16 rounded-xl overflow-hidden bg-gray-100 flex items-center justify-center text-3xl border">
              <img v-if="selectedPhotoUrl" :src="selectedPhotoUrl" class="w-full h-full object-cover" />
              <span v-else>{{ selected.avatar }}</span>
            </div>
            <button @click="uploadPhoto('elderly')" class="absolute -bottom-1 -right-1 w-6 h-6 bg-primary-600 text-white rounded-full text-xs flex items-center justify-center shadow hover:bg-primary-700">
              <i class="fas fa-camera"></i>
            </button>
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-xl font-bold text-gray-800">{{ selected.name }}</div>
            <div class="text-sm text-gray-500">{{ selected.age }}岁 · {{ selected.condition }}</div>
          </div>
        </div>
        <div class="flex-shrink-0 mb-3">
          <label class="text-sm font-medium text-gray-500 mb-1.5 block"><i class="fas fa-tags mr-1"></i>标签</label>
          <div class="flex flex-wrap gap-1.5 mb-2">
            <span v-for="(t,i) in (selected.traits||[])" :key="i"
              class="inline-flex items-center gap-1 px-3 py-1.5 bg-primary-100 text-primary-600 rounded-full text-sm">
              {{ t }}
              <button @click="removeTrait(i)" class="text-primary-400 hover:text-red-500 text-xs leading-none"><i class="fas fa-times"></i></button>
            </span>
          </div>
          <div class="flex gap-2">
            <input v-model="newTrait" @keydown.enter="addTrait" placeholder="添加标签"
              class="flex-1 px-3 py-1.5 text-sm bg-white border border-gray-200 rounded-xl outline-none focus:border-primary-400" />
            <button @click="addTrait" :disabled="!newTrait.trim()"
              class="px-3 py-1.5 text-sm bg-primary-100 text-primary-600 rounded-xl hover:bg-primary-200 transition-colors">
              <i class="fas fa-plus"></i>
            </button>
          </div>
        </div>
        <div class="flex-1 flex flex-col overflow-hidden min-h-0">
          <!-- Children Section -->
          <div class="flex-shrink-0 mb-2">
            <button @click="showChildren=!showChildren" class="flex items-center gap-2 text-sm font-medium text-gray-500 mb-1.5">
              <i class="fas fa-users"></i>子女 ({{ children.length }})
              <i class="fas fa-chevron-down text-xs transition-transform" :class="showChildren?'rotate-0':'-rotate-90'"></i>
            </button>
            <div v-if="showChildren" class="space-y-2">
              <div v-for="c in children" :key="c.id"
                class="flex items-center gap-2 px-3 py-2 bg-white rounded-xl border border-gray-100">
                <div class="relative flex-shrink-0">
                  <div class="w-9 h-9 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center text-base border">
                    <img v-if="c.photo" :src="c.photo" class="w-full h-full object-cover" />
                    <span v-else>{{ c.avatar }}</span>
                  </div>
                  <button @click="uploadChildPhoto(c)" class="absolute -bottom-1 -right-1 w-4 h-4 bg-primary-500 text-white rounded-full text-[8px] flex items-center justify-center shadow hover:bg-primary-600">
                    <i class="fas fa-camera"></i>
                  </button>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="text-sm font-medium text-gray-800">{{ c.name }} <span class="text-xs text-gray-400 font-normal">({{ c.relationship||'子女' }})</span></div>
                  <div class="text-xs text-gray-400 truncate">{{ c.personality || '暂无描述' }}</div>
                </div>
                <button @click="editChild(c)" class="text-primary-400 hover:text-primary-600 text-xs"><i class="fas fa-edit"></i></button>
                <button @click="deleteChild(c.id)" class="text-gray-300 hover:text-red-400 text-xs"><i class="fas fa-times"></i></button>
              </div>
              <button @click="openAddChild" class="flex items-center gap-1.5 text-xs text-primary-500 hover:text-primary-700">
                <i class="fas fa-plus"></i>添加子女
              </button>
            </div>
          </div>
          <!-- Profile Text -->
          <div class="flex items-center justify-between mb-1.5 flex-shrink-0">
            <label class="text-sm font-medium text-gray-400"><i class="fas fa-file-lines mr-1"></i>画像文字</label>
            <button @click="saveProfile" :disabled="savingProfile"
              class="text-xs px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-1">
              <i v-if="savingProfile" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-floppy-disk"></i>
              保存画像
            </button>
          </div>
          <textarea readonly :value="profileText"
            class="flex-1 w-full bg-primary-50/30 border border-primary-100 rounded-xl p-3 text-sm text-gray-600 resize-none font-mono leading-relaxed outline-none" />
        </div>
      </div>

      <!-- Right: Task Creation + Schedule -->
      <div class="flex-1 flex flex-col gap-5 overflow-y-auto min-w-0 pr-1">
        <!-- Task Creation Form -->
        <div class="flex-shrink-0 bg-white/70 backdrop-blur-sm rounded-2xl border border-white/50 shadow p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold text-gray-800"><i class="fas fa-clipboard-list mr-2"></i>创建照护任务</h3>
            <span class="text-sm text-gray-400 bg-gray-100 px-3 py-1 rounded-full">{{ selected.name }}</span>
          </div>
          <!-- Video Mode Selection -->
          <div class="flex gap-2 mb-4">
            <button @click="videoMode='reminder'"
              :class="['flex-1 py-3 px-2 rounded-xl border-2 transition-all text-center',
                videoMode==='reminder'?'border-primary-500 bg-primary-50 shadow-sm':'border-gray-200 bg-white/70 hover:border-gray-300']">
              <i class="fas fa-bell text-xl mb-0.5" :class="videoMode==='reminder'?'text-primary-500':'text-gray-400'"></i>
              <div class="font-bold text-xs" :class="videoMode==='reminder'?'text-primary-700':'text-gray-600'">提醒</div>
              <div class="text-[10px] text-gray-400">AI匹配最佳视频</div>
            </button>
            <button @click="videoMode='digital'"
              :class="['flex-1 py-3 px-2 rounded-xl border-2 transition-all text-center',
                videoMode==='digital'?'border-blue-500 bg-blue-50 shadow-sm':'border-gray-200 bg-white/70 hover:border-gray-300']">
              <i class="fas fa-robot text-xl mb-0.5" :class="videoMode==='digital'?'text-blue-500':'text-gray-400'"></i>
              <div class="font-bold text-xs" :class="videoMode==='digital'?'text-blue-700':'text-gray-600'">数字人视频</div>
              <div class="text-[10px] text-gray-400">无法交互</div>
            </button>
            <button @click="videoMode='interactive'"
              :class="['flex-1 py-3 px-2 rounded-xl border-2 transition-all text-center',
                videoMode==='interactive'?'border-accent bg-amber-50 shadow-sm':'border-gray-200 bg-white/70 hover:border-gray-300']">
              <i class="fas fa-microphone text-xl mb-0.5" :class="videoMode==='interactive'?'text-accent':'text-gray-400'"></i>
              <div class="font-bold text-xs" :class="videoMode==='interactive'?'text-amber-700':'text-gray-600'">可交互视频</div>
              <div class="text-[10px] text-gray-400">支持语音互动</div>
            </button>
          </div>
          <!-- Reminder presets (reminder mode only) -->
          <div v-if="videoMode==='reminder'" class="mb-3">
            <div class="grid grid-cols-2 gap-2">
              <button v-for="(p,i) in reminderPresets" :key="i"
                @click="quickReminder(p)"
                class="px-4 py-3 bg-white border border-gray-200 rounded-xl text-left hover:border-primary-300 hover:shadow-sm transition-all group"
                :disabled="pushingPreset === i">
                <div class="font-bold text-sm text-gray-700 group-hover:text-primary-700">{{ p.icon }} {{ p.label }}</div>
                <div class="text-xs text-gray-400 mt-0.5 line-clamp-2">{{ p.content }}</div>
              </button>
            </div>
          </div>
          <!-- Digital human photo upload (digital/interactive mode) -->
          <div v-if="videoMode==='digital'||videoMode==='interactive'" class="mb-3 flex items-center gap-3">
            <button @click="dhPhotoInput?.click()"
              class="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm text-gray-600 hover:border-primary-300 hover:text-primary-600 transition-all flex items-center gap-2">
              <i class="fas fa-user-circle"></i>
              {{ dhPhotoName || '上传数字人头像' }}
            </button>
            <span v-if="dhPhotoUrl" class="text-xs text-green-600"><i class="fas fa-check-circle mr-1"></i>已上传</span>
            <span v-else class="text-xs text-gray-400">必填，用于生成数字人视频</span>
          </div>
          <textarea v-model="taskContent" rows="3" placeholder="例如：提醒王奶奶晚上8点吃降压药"
            class="w-full bg-warm-50 border border-warm-200 rounded-xl p-4 text-base text-gray-700 resize-none outline-none focus:border-primary-300 placeholder-gray-300 leading-relaxed" />
          <div class="mt-3 flex items-center gap-3">
            <span class="text-sm text-gray-500 flex-shrink-0"><i class="fas fa-user-tie mr-1"></i>数字人身份:</span>
            <select v-model="selectedChild" class="flex-1 text-base bg-white border border-gray-200 rounded-xl px-4 py-2 outline-none focus:border-primary-400">
              <option :value="null">AI 默认助手</option>
              <option v-for="c in children" :key="c.id" :value="c">{{ c.avatar }} {{ c.name }}（{{ c.relationship||'子女' }}）</option>
            </select>
          </div>
          <div class="flex items-center gap-6 mt-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="taskMode" value="immediate" class="w-4 h-4 text-primary-600" />
              <span class="text-base text-gray-700"><i class="fas fa-bolt mr-1"></i>立即推送</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="taskMode" value="scheduled" class="w-4 h-4 text-primary-600" />
              <span class="text-base text-gray-700"><i class="fas fa-clock mr-1"></i>定时推送</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" v-model="taskMode" value="daily" class="w-4 h-4 text-primary-600" />
              <span class="text-base text-gray-700"><i class="fas fa-rotate mr-1"></i>每日重复</span>
            </label>
          </div>
          <div v-if="taskMode !== 'immediate'" class="mt-3 flex items-center gap-3">
            <span class="text-base text-gray-500">定时时间:</span>
            <input type="time" v-model="taskTime"
              class="text-base bg-white border border-gray-200 rounded-xl px-4 py-2 outline-none focus:border-primary-400" />
          </div>
          <div class="flex items-center gap-4 mt-4">
            <button @click="createTask" :disabled="!taskContent.trim() || creating"
              class="btn-primary text-base px-6 py-3 flex items-center gap-2">
              <i v-if="creating" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-plus"></i>
              创建任务
            </button>
            <span v-if="createResult" class="text-base" :class="createResult.success ? 'text-green-600' : 'text-red-600'">
              {{ createResult.msg }}
            </span>
          </div>
        </div>

        <!-- Task Schedule List -->
        <div class="bg-white/70 backdrop-blur-sm rounded-2xl border border-white/50 shadow p-5">
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold text-gray-800"><i class="fas fa-calendar mr-2"></i>任务时间表</h3>
            <span class="text-sm text-gray-400">{{ tasks.length }} 个任务</span>
          </div>
          <div class="space-y-3">
            <div v-if="tasks.length === 0" class="text-center text-gray-400 text-base pt-12">暂无任务</div>
            <div v-for="t in tasks" :key="t.id"
              class="p-4 rounded-xl border transition-all"
              :class="t.pushed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-100 shadow-sm'">
              <div class="flex items-start gap-3">
                <span class="text-2xl flex-shrink-0">{{ t.elderly_avatar }}</span>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-3">
                    <p class="font-medium text-gray-800 truncate">{{ t.rewritten || t.content }}</p>
                    <span class="text-sm px-2 py-0.5 rounded-full flex-shrink-0" :class="statusClass(t)">{{ statusLabel(t) }}</span>
                  </div>
                  <div class="flex items-center gap-3 mt-1 text-sm text-gray-400">
                    <span>{{ modeLabel(t.mode) }}</span>
                    <span>· {{ videoModeLabel(t.video_mode) }}</span>
                    <span v-if="t.scheduled_time">· {{ t.scheduled_time }}</span>
                    <span>· {{ t.elderly_name }}</span>
                    <span v-if="t.pushed_at" class="text-green-500">· <i class="fas fa-check-circle mr-0.5"></i>{{ formatTime(t.pushed_at) }}</span>
                  </div>
                </div>
                <button @click="deleteTask(t.id)" class="text-gray-300 hover:text-red-400 transition-colors flex-shrink-0 text-lg">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="flex-1 flex items-center justify-center text-gray-400 text-lg">
      <i class="fas fa-arrow-up mr-2"></i>请从上方选择一个老人
    </div>

    <!-- Add Elderly Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" @click.self="showAddModal=false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-[420px] max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800"><i class="fas fa-plus mr-2"></i>添加老人</h3>
          <button @click="showAddModal=false" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
        </div>
        <div class="space-y-3">
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">姓名</label>
            <input v-model="addForm.name" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-600 mb-1">年龄</label>
              <input v-model.number="addForm.age" type="number" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
            </div>
            <div class="w-20">
              <label class="block text-sm font-medium text-gray-600 mb-1">头像</label>
              <input v-model="addForm.avatar" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">健康状况</label>
            <input v-model="addForm.condition" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">标签 (逗号分隔)</label>
            <input v-model="addForm.traitsInput" placeholder="例如: 健忘, 温和, 喜欢下棋"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button @click="submitAddElderly" :disabled="addSubmitting||!addForm.name.trim()"
            class="flex-1 bg-primary-600 text-white rounded-xl py-3 font-medium hover:bg-primary-700 transition-colors">
            <i v-if="addSubmitting" class="fas fa-spinner fa-spin mr-1"></i>创建
          </button>
          <button @click="showAddModal=false" class="px-6 py-3 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50">取消</button>
        </div>
      </div>
    </div>

    <!-- Child Add/Edit Modal -->
    <div v-if="childModal" class="fixed inset-0 bg-black/40 z-50 flex items-center justify-center" @click.self="childModal=false">
      <div class="bg-white rounded-2xl shadow-xl p-6 w-[400px]">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-800"><i class="fas fa-child mr-2"></i>{{ editingChild ? '编辑子女' : '添加子女' }}</h3>
          <button @click="childModal=false" class="text-gray-400 hover:text-gray-600"><i class="fas fa-times"></i></button>
        </div>
        <div class="space-y-3">
          <div class="flex gap-3">
            <div class="flex-1">
              <label class="block text-sm font-medium text-gray-600 mb-1">姓名</label>
              <input v-model="childForm.name" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
            </div>
            <div class="w-20">
              <label class="block text-sm font-medium text-gray-600 mb-1">头像</label>
              <input v-model="childForm.avatar" class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">关系（如：儿子、女儿）</label>
            <input v-model="childForm.relationship" placeholder="儿子/女儿"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600 mb-1">性格特征 / 备注</label>
            <textarea v-model="childForm.personality" rows="2" placeholder="例如：在外地工作，性格温和有耐心，每周视频通话"
              class="w-full px-4 py-2.5 rounded-xl border border-gray-200 text-base outline-none focus:border-primary-400 resize-none" />
          </div>
        </div>
        <div class="flex gap-3 mt-5">
          <button @click="saveChild" :disabled="!childForm.name.trim()"
            class="flex-1 bg-primary-600 text-white rounded-xl py-3 font-medium hover:bg-primary-700 transition-colors">
            <i class="fas fa-check mr-1"></i>{{ editingChild ? '保存' : '添加' }}
          </button>
          <button @click="childModal=false" class="px-6 py-3 border border-gray-200 rounded-xl text-gray-600 hover:bg-gray-50">取消</button>
        </div>
      </div>
    </div>
    <!-- Hidden file input for photo uploads -->
    <input ref="fileInput" type="file" accept="image/*" class="hidden" @change="onFileSelected" />
    <input ref="videoFileInput" type="file" accept="video/*" class="hidden" @change="onVideoSelected" />
    <input ref="dhPhotoInput" type="file" accept="image/*" class="hidden" @change="onDhPhotoSelected" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAuth, logout } from '../auth'

const router = useRouter()
const auth = getAuth()
const elderlyList = ref([])
const selected = ref(null)
const taskContent = ref('')
const taskMode = ref('immediate')
const taskTime = ref('20:00')
const creating = ref(false)
const createResult = ref(null)
const tasks = ref([])
const newTrait = ref('')
const savingProfile = ref(false)
const searchQuery = ref('')
const showAddModal = ref(false)
const addSubmitting = ref(false)
const addForm = ref({ name:'', age:70, avatar:'👴', condition:'', traitsInput:'' })
const children = ref([])
const showChildren = ref(true)
const childModal = ref(false)
const editingChild = ref(null)
const selectedChild = ref(null)
const childForm = ref({ name:'', avatar:'👤', relationship:'', personality:'' })
const selectedPhotoUrl = ref('')
const fileInput = ref(null)
const videoFileInput = ref(null)
const dhPhotoInput = ref(null)
const videoMode = ref('reminder')
const pushingPreset = ref(null)
const customVideoUrl = ref(null)
const customVideoName = ref(null)
const dhPhotoUrl = ref(null)
const dhPhotoName = ref(null)
const uploadingVideo = ref(false)
let pendingUploadTarget = null
let searchTimer = null

function selectElder(elder) {
  selected.value = elder
  selectedChild.value = null
  loadChildren(elder.id)
}
async function loadChildren(elderId) {
  try { const r=await fetch(`/api/elderly/${elderId}/children`); const d=await r.json(); children.value=d.children } catch(_) {}
}

function addTrait() {
  const t = newTrait.value.trim()
  if (!t) return
  if (!selected.value.traits) selected.value.traits = []
  selected.value.traits.push(t)
  newTrait.value = ''
}
function removeTrait(i) {
  selected.value.traits.splice(i, 1)
}
async function saveProfile() {
  const e = selected.value
  if (!e) return
  savingProfile.value = true
  try {
    const res = await fetch(`/api/admin/users/${e.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name:e.name, role:e.role, age:e.age, avatar:e.avatar, condition:e.condition, traits:e.traits }),
    })
    if (!res.ok) throw new Error('保存失败')
  } catch (_) {}
  finally { savingProfile.value = false }
}

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(searchElderly, 300)
}
async function searchElderly() {
  try {
    const res = await fetch(`/api/users/elderly?q=${encodeURIComponent(searchQuery.value)}`)
    const d = await res.json()
    elderlyList.value = d.users
  } catch (_) {}
}
async function submitAddElderly() {
  const f = addForm.value
  if (!f.name.trim()) return
  addSubmitting.value = true
  try {
    const traits = f.traitsInput ? f.traitsInput.split(',').map(s=>s.trim()).filter(Boolean) : []
    const res = await fetch('/api/admin/users', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ name:f.name, role:'elderly', password:'123456', avatar:f.avatar||'👴', age:f.age||70, condition:f.condition||'', traits }),
    })
    const d = await res.json()
    if (d.success) {
      showAddModal.value = false
      addForm.value = { name:'', age:70, avatar:'👴', condition:'', traitsInput:'' }
      searchQuery.value = ''
      await searchElderly()
      selectElder(d.user)
    }
  } catch (_) {}
  finally { addSubmitting.value = false }
}

function openAddChild() {
  editingChild.value = null
  childForm.value = { name:'', avatar:'👤', relationship:'', personality:'' }
  childModal.value = true
}
function editChild(c) {
  editingChild.value = c
  childForm.value = { name:c.name, avatar:c.avatar, relationship:c.relationship||'', personality:c.personality||'' }
  childModal.value = true
}
async function saveChild() {
  if (!childForm.value.name.trim() || !selected.value) return
  const body = { name:childForm.value.name, avatar:childForm.value.avatar||'👤', relationship:childForm.value.relationship, personality:childForm.value.personality }
  try {
    let res
    if (editingChild.value) {
      res = await fetch(`/api/children/${editingChild.value.id}`, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) })
    } else {
      res = await fetch(`/api/elderly/${selected.value.id}/children`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body) })
    }
    const d = await res.json()
    if (d.success) childModal.value = false
  } catch(_) {}
  finally { loadChildren(selected.value.id) }
}
async function deleteChild(id) {
  if (!confirm('确定删除此子女？')) return
  try { await fetch(`/api/children/${id}`, { method:'DELETE' }); loadChildren(selected.value.id) } catch(_) {}
}

function uploadPhoto(target) {
  pendingUploadTarget = target
  fileInput.value?.click()
}
function uploadChildPhoto(child) {
  pendingUploadTarget = child
  fileInput.value?.click()
}
async function onFileSelected(e) {
  const file = e.target.files?.[0]
  if (!file || !pendingUploadTarget) return
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch('/api/upload', { method:'POST', body: form })
    const d = await res.json()
    if (!d.success) return
    if (pendingUploadTarget === 'elderly') {
      selectedPhotoUrl.value = d.url
    } else if (pendingUploadTarget?.id) {
      // Update child's photo via API
      await fetch(`/api/children/${pendingUploadTarget.id}`, {
        method:'PUT',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ photo: d.url })
      })
      loadChildren(selected.value.id)
    }
  } catch(_) {}
  finally { pendingUploadTarget = null; e.target.value = '' }
}

async function onVideoSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  uploadingVideo.value = true
  customVideoName.value = file.name
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch('/api/upload', { method:'POST', body: form })
    const d = await res.json()
    if (d.success) {
      customVideoUrl.value = d.url
    } else {
      customVideoName.value = null
    }
  } catch (_) {
    customVideoName.value = null
  } finally {
    uploadingVideo.value = false
    e.target.value = ''
  }
}

async function onDhPhotoSelected(e) {
  const file = e.target.files?.[0]
  if (!file) return
  dhPhotoName.value = file.name
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch('/api/upload', { method:'POST', body: form })
    const d = await res.json()
    if (d.success) {
      dhPhotoUrl.value = d.url
    } else {
      dhPhotoName.value = null
    }
  } catch (_) {
    dhPhotoName.value = null
  } finally {
    e.target.value = ''
  }
}

const profileText = computed(() => {
  const e = selected.value
  if (!e) return ''
  let text = `姓名：${e.name}\n年龄：${e.age}岁\n健康状况：${e.condition}\n特点：${(e.traits||[]).join('、') || '暂无标签'}`
  if (children.value.length) {
    text += '\n子女：'
    children.value.forEach(c => { text += `\n  ${c.avatar} ${c.name}（${c.relationship||'子女'}）- ${c.personality||'暂无描述'}` })
  }
  return text
})

function modeLabel(m) { return { immediate:'🚀 即时', scheduled:'⏰ 定时', daily:'🔁 每日' }[m]||m }
function videoModeLabel(m) { return { reminder:'🔔 提醒', digital:'🤖 数字人', interactive:'🎤 可交互' }[m]||m||'🔔 提醒' }
function statusLabel(t) {
  if (t.pushed) return '<i class="fas fa-check-circle mr-1"></i>已推送'
  if (t.mode === 'immediate') return '⏳ 待推送'
  return `⏳ ${t.scheduled_time||''}`
}
function statusClass(t) { return t.pushed ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700' }
function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`
}

function handleLogout() { logout(); router.push('/') }

async function createTask() {
  if (!taskContent.value.trim() || !selected.value) return
  creating.value = true; createResult.value = null
  const payload = {
    elderly_id: selected.value.id, elderly_name: selected.value.name, elderly_avatar: selected.value.avatar,
    content: taskContent.value, profile_text: profileText.value,
    mode: taskMode.value, scheduled_time: taskMode.value === 'immediate' ? null : taskTime.value,
    child_id: selectedChild.value?.id || null,
    child_name: selectedChild.value?.name || null,
    photo_url: selectedPhotoUrl.value || null,
    child_photo_url: selectedChild.value?.photo || null,
    video_mode: videoMode.value,
    custom_video_url: customVideoUrl.value,
    digital_human_photo_url: dhPhotoUrl.value,
  }
  try {
    const res = await fetch('/api/tasks', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    if (!res.ok) {
      const err = await res.json()
      createResult.value = { success:false, msg:`❌ ${err.detail || '内容不合法，已被拦截'}` }
      return
    }
    const data = await res.json()
    tasks.value.unshift(data.task)
    createResult.value = { success:true, msg:`✅ 任务 #${data.task.id} 已创建` }
    if (data.task.video_mode === 'reminder') console.log('[DeepSeek] 匹配视频:', data.task.video_url)
    taskContent.value = ''
  } catch (e) { createResult.value = { success:false, msg:`❌ 网络错误: ${e.message}` }
  } finally { creating.value = false }
}
async function deleteTask(id) {
  try { await fetch(`/api/tasks/${id}`, { method:'DELETE' }); tasks.value = tasks.value.filter(t => t.id !== id) }
  catch (_) {}
}

const reminderPresets = [
  { icon:'💊', label:'吃药提醒', content:'到吃药时间了，先把药吃了，再喝点温水~' },
  { icon:'🏃', label:'康复运动', content:'康复时间到啦，我们慢慢活动一下，不着急~' },
  { icon:'🍚', label:'吃饭提醒', content:'该吃饭啦，今天的饭菜很香哦，趁热吃~' },
  { icon:'🌙', label:'睡觉提醒', content:'今天辛苦啦，早点休息，明天精神会更好~' },
  { icon:'💕', label:'暖心问候', content:'今天过得怎么样？要照顾好自己，我一直在~' },
  { icon:'☀️', label:'早安问候', content:'早上好呀，又是美好的一天，记得吃早餐哦~' },
]

async function quickReminder(preset) {
  if (!selected.value) return
  pushingPreset.value = reminderPresets.indexOf(preset)
  const payload = {
    elderly_id: selected.value.id, elderly_name: selected.value.name, elderly_avatar: selected.value.avatar,
    content: preset.content, profile_text: profileText.value,
    mode: 'immediate', scheduled_time: null,
    child_id: null, child_name: null,
    photo_url: null, child_photo_url: null,
    video_mode: 'reminder',
    custom_video_url: null,
    digital_human_photo_url: null,
  }
  try {
    const res = await fetch('/api/tasks', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    if (!res.ok) {
      const err = await res.json()
      createResult.value = { success:false, msg:`❌ ${err.detail || '发送失败'}` }
      return
    }
    const data = await res.json()
    tasks.value.unshift(data.task)
    console.log('[DeepSeek] 匹配视频:', data.task.video_url)
    createResult.value = { success:true, msg:`✅ 已推送「${preset.label}」` }
  } catch (e) {
    createResult.value = { success:false, msg:`❌ 网络错误: ${e.message}` }
  } finally {
    pushingPreset.value = null
  }
}

onMounted(async () => {
  try {
    const [elderRes, taskRes] = await Promise.all([
      fetch('/api/users/elderly'),
      fetch('/api/tasks'),
    ])
    const elderData = await elderRes.json()
    const taskData = await taskRes.json()
    elderlyList.value = elderData.users
    tasks.value = taskData.tasks
    if (elderlyList.value.length) {
      selected.value = elderlyList.value[0]
      loadChildren(selected.value.id)
    }
  } catch (_) {}
})
</script>
