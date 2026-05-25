# 亲伴 AI — 老年人 AI 照护陪伴助手

面向护工的老年人 AI 照护陪伴系统。护工创建照护任务，系统通过数字人视频向老人推送关怀提醒，支持语音交互和安全审查。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Tailwind CSS 3 + Vue Router 4 + Font Awesome Free 7 |
| 后端 | FastAPI + SQLite + uvicorn |
| 运行环境 | Python 3.10+ (uv 管理) + Node.js 18+ |
| 外部 API | OpenAI Sora（数字人视频生成）、Lingya AI（内容安全审查）、可接入 STT/TTS |

## 快速开始

### 1. 克隆 & 安装依赖

```bash
git clone <repo-url>
cd careAI

# 后端依赖（使用 uv）
cd backend
uv sync
cd ..

# 前端依赖
cd frontend
npm install
cd ..
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入必要的 API Key：

| 变量 | 用途 | 是否必填 |
| --- | --- | --- |
| `OPENAI_API_KEY` | OpenAI Sora 视频生成（数字人） | 生成数字人视频时需要 |
| `LINGYA_API_KEY` | 灵崖AI 内容安全审查 | 可选，不配则跳过 LLM 审查 |
| `STT_API_KEY` | 语音识别 | 可选，不配则使用模拟数据 |
| `LLM_API_KEY` | 内容改写 / 数字人回复 | 可选 |

> `.env` 已在 `.gitignore` 中，不会提交到仓库。

### 3. 启动开发服务器

```bash
cd frontend
npm run dev
```

这会将同时启动：
- 后端 API → `http://localhost:8000`
- 前端页面 → `http://localhost:5173`

### 4. 初始账号

系统首次启动自动创建以下账号：

| 角色 | 用户名 | 密码 | 说明 |
| --- | --- | --- | --- |
| 管理员 | 管理员 | admin123 | 管理所有用户 |
| 护工 | 张三 | 123456 | 创建任务、管理老人 |
| 老人 | 王奶奶 | 123456 | 接收照护消息 |
| 老人 | 李爷爷 | 123456 | 接收照护消息 |

## 项目结构

```
careAI/
├── backend/
│   ├── main.py                  # FastAPI 主服务（API + SQLite + 审查）
│   ├── video_review.py          # 视频安全审查（灵崖AI）
│   ├── digital_human_gen.py     # 数字人视频生成（OpenAI Sora）
│   └── qinban.db                # SQLite 数据库（自动创建）
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── LoginPage.vue          # 登录页
│   │   │   ├── CaregiverDashboard.vue # 护工工作台
│   │   │   ├── ElderlyPortal.vue      # 老人终端
│   │   │   ├── ElderlyPlayer.vue      # 视频播放器
│   │   │   └── AdminPage.vue          # 管理员页面
│   │   ├── router/index.js            # 路由定义
│   │   └── auth.js                    # 前端认证
│   ├── package.json
│   └── vite.config.js
├── videos/                      # 预制视频文件
├── uploads/                     # 上传的图片/视频
├── .env                         # 环境变量（不提交）
├── .env.example                 # 环境变量模板
└── README.md
```

## 功能说明

### 护工端

- **搜索 & 选择老人** — 从已注册的老人列表中搜索、选择
- **老人画像** — 编辑标签、上传照片、管理子女信息
- **创建照护任务** — 填写任务内容，选择视频模式：
  - **预制视频** — 播放已有视频文件，可上传自定义视频
  - **数字人视频** — 基于上传的头像生成数字人视频，不可交互
  - **可交互视频** — 数字人视频 + 语音互动
- **推送方式** — 立即推送 / 定时推送 / 每日重复
- **内容安全审查** — 提交任务时自动审查（关键词 + AI）

### 老人端

- **推荐视频** — 浏览和播放预设视频
- **任务推送** — 护工推送的任务自动全屏播放
- **语音互动** — 可交互模式下支持语音输入和 AI 回复
- **安全打断** — 检测到危险内容时自动中断播放

### 管理员端

- 用户 CRUD 管理（护工 / 老人）
- 账号统计

## API 概览

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/login` | 登录 |
| GET | `/api/users/elderly` | 老人列表（支持模糊搜索） |
| POST/PUT/DELETE | `/api/admin/users` | 管理员用户管理 |
| POST | `/api/tasks` | 创建照护任务 |
| GET | `/api/tasks/pending` | 获取待推送任务 |
| POST | `/api/tasks/ack` | 确认任务已送达 |
| POST | `/api/upload` | 上传图片/视频 |
| POST | `/api/audio/transcribe` | 语音转文字 |
| GET/POST/PUT/DELETE | `/api/elderly/{id}/children` | 子女信息管理 |

## 部署

### 生产构建

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/`，可用任意静态服务器托管前端。后端需独立部署 uvicorn：

```bash
cd backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker（可选）

```dockerfile
# 可自行编写 Dockerfile，分为前端（nginx）和后端（uvicorn）两个容器
```

## 协作约定

- 使用 `uv` 管理 Python 依赖，`npm` 管理前端依赖
- 不要提交 `.env`、`*.db`、`videos/`、`uploads/`、`node_modules/`
- 新增外部 API 时，密钥统一放在 `.env`，在 `.env.example` 添加占位
- 前端颜色体系：`primary-600: #6B4E8A`、`accent: #E8923E`

## License

MIT
