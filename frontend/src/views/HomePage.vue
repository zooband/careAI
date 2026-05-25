<template>
  <div class="h-screen w-screen overflow-hidden gradient-bg flex flex-col">
    <!-- Header -->
    <header class="flex-shrink-0 px-6 sm:px-10 py-3 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-2xl">💜</span>
        <span class="text-lg font-bold text-primary-700">家有 AI 宝</span>
      </div>
      <div class="flex items-center gap-2 text-xs text-gray-400">
        <span class="hidden sm:inline">AI 亲情陪伴助手 · 由家人授权创建</span>
        <span class="w-1.5 h-1.5 rounded-full bg-green-400 inline-block"></span>
      </div>
    </header>

    <!-- Main content: fill remaining height -->
    <div class="flex-1 flex items-center justify-center px-6 sm:px-10 overflow-hidden">
      <div class="flex items-center gap-8 lg:gap-16 w-full max-w-6xl">
        <!-- Left: Text -->
        <div class="flex-1 min-w-0">
          <div class="inline-block px-3 py-1.5 bg-primary-100 text-primary-700 rounded-xl text-xs font-medium mb-4">
            🏥 银发养老 · 亲情数字陪伴
          </div>
          <h1 class="text-3xl sm:text-4xl lg:text-5xl font-black text-gray-900 leading-tight mb-3">
            谁说老了
            <span class="text-accent">就没人管？</span>
          </h1>
          <p class="text-sm sm:text-base text-gray-500 leading-relaxed mb-5">
            "AI"时代，给家人多点爱。<br />
            基于家人授权照片生成数字人形象，
            为老人提供情绪陪伴、生活提醒与照护协同。
          </p>
          <div class="flex flex-wrap gap-3">
            <router-link to="/caregiver" class="btn-primary flex items-center gap-2 px-6 py-3 text-sm">
              <span>🔧</span> 护工工作台
            </router-link>
            <router-link to="/elderly" class="btn-accent flex items-center gap-2 px-6 py-3 text-sm">
              <span>📺</span> 老人终端
            </router-link>
          </div>
          <div class="mt-4 flex items-center gap-3 text-xs text-gray-400">
            <span>✓ 家人授权</span>
            <span>✓ AI 标识</span>
            <span>✓ 内容审核</span>
          </div>
        </div>

        <!-- Right: Device mockup -->
        <div class="flex-shrink-0 hidden md:block">
          <div class="relative w-48 lg:w-56">
            <div class="bg-gray-900 rounded-2xl p-2 shadow-2xl">
              <div class="bg-gradient-to-br from-primary-100 via-warm-50 to-primary-200 rounded-xl overflow-hidden aspect-[9/16] relative">
                <div class="bg-primary-700 text-white text-[10px] px-3 py-1.5 flex items-center justify-between">
                  <span>家有 AI 宝</span>
                  <span>09:41</span>
                </div>
                <div class="p-3 flex flex-col items-center justify-center" style="height:calc(100% - 26px)">
                  <div class="text-4xl mb-2">👵</div>
                  <div class="text-primary-700 font-bold text-xs mb-2">王奶奶 · 78岁</div>
                  <div class="bg-primary-600/10 rounded-xl p-2 w-full text-center mb-2">
                    <div class="text-primary-700 text-[10px] font-medium mb-1">💬 数字人提醒</div>
                    <div class="text-primary-800 text-xs">"奶奶，到吃药时间啦~"</div>
                  </div>
                  <div class="bg-accent/10 rounded-xl p-1.5 w-full text-center">
                    <div class="text-accent-dark text-[10px]">⏰ 服药提醒 · 20:00</div>
                  </div>
                </div>
                <div class="absolute bottom-0 left-0 right-0 bg-black/40 text-white/70 text-[8px] text-center py-0.5">
                  AI 亲情陪伴助手 · 由家人授权创建
                </div>
              </div>
            </div>
            <div class="absolute -top-2 -right-2 bg-white rounded-xl px-3 py-1.5 shadow text-xs font-medium text-primary-700">
              💜 今天也要按时吃药哦~
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="flex-shrink-0 text-center pb-3 text-xs text-gray-400">
      家有 AI 宝 · 面向银发养老场景的亲情数字陪伴 Agent
    </div>
  </div>
</template>
