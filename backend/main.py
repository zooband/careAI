"""
亲伴 AI - Backend API
  - SQLite user store with auth
  - Task management (immediate/scheduled/daily)
  - Content review, video generation
  - Admin user CRUD
"""
import os, random, json, sqlite3
from datetime import datetime, date
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load .env from project root (parent of backend/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

app = FastAPI(title="亲伴 AI API", version="0.2.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_DIR = os.path.join(os.path.dirname(BASE_DIR), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)
app.mount("/api/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")

UPLOADS_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# ── SQLite Database ──────────────────────────────────────
DB_PATH = os.path.join(BASE_DIR, "qinban.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT NOT NULL DEFAULT '123456',
            role TEXT NOT NULL CHECK(role IN ('admin','caregiver','elderly')),
            avatar TEXT DEFAULT '👤',
            age INTEGER DEFAULT 70,
            condition TEXT DEFAULT '',
            traits TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
        CREATE TABLE IF NOT EXISTS children (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            elderly_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            avatar TEXT DEFAULT '👤',
            photo TEXT DEFAULT '',
            relationship TEXT DEFAULT '',
            personality TEXT DEFAULT '',
            voice_profile TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (elderly_id) REFERENCES users(id)
        );
    """)
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        conn.executescript("""
            INSERT INTO users (name,password,role,avatar,age,condition,traits) VALUES
                ('管理员','admin123','admin','👤',30,'系统管理员','[]'),
                ('张三','123456','caregiver','👨',35,'高级护工','["耐心","专业"]'),
                ('王奶奶','123456','elderly','👵',78,'阿尔兹海默症早期','["健忘","温和","喜欢听戏曲","不习惯被命令"]'),
                ('李爷爷','123456','elderly','👴',82,'独居·轻度抑郁倾向','["思念子女","喜欢下棋","不太爱说话"]');
            INSERT INTO children (elderly_id,name,avatar,relationship,personality) VALUES
                (3,'王小明','👨','儿子','在外地工作，每周视频通话，性格温和有耐心'),
                (4,'李华','👩','女儿','住在同城，每周回家看望，性格细心体贴');
        """)
    conn.commit()
    conn.close()

init_db()

# ── Pydantic models ──────────────────────────────────────
class LoginRequest(BaseModel):
    name: str
    password: str
    role: str  # "caregiver" | "elderly" | "admin"

class UserCreateRequest(BaseModel):
    name: str
    password: str = "123456"
    role: str
    avatar: str = "👤"
    age: int = 70
    condition: str = ""
    traits: list[str] = []

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    avatar: Optional[str] = None
    age: Optional[int] = None
    condition: Optional[str] = None
    traits: Optional[list[str]] = None

class ReviewRequest(BaseModel):
    text: str
class ReviewResult(BaseModel):
    passed: bool; risk_level: str; issues: list[str]; rewritten_text: Optional[str] = None

class TranscribeResponse(BaseModel):
    text: str
    safe: bool
    issues: list[str]
    rewritten_text: Optional[str] = None

class VideoRequest(BaseModel):
    scenario_id: str; reminder_type: str; caregiver_text: str; elderly_profile: Optional[dict] = None

class CareReminderRequest(BaseModel):
    profile_text: str; prompt: str

class TaskCreateRequest(BaseModel):
    elderly_id: int; elderly_name: str; elderly_avatar: str = "👵"
    content: str; profile_text: str; mode: str; scheduled_time: Optional[str] = None
    child_id: Optional[int] = None; child_name: Optional[str] = None
    photo_url: Optional[str] = None; child_photo_url: Optional[str] = None
    video_mode: str = "prerecorded"
    custom_video_url: Optional[str] = None

class ChildCreateRequest(BaseModel):
    name: str; avatar: str = "👤"; photo: str = ""; relationship: str = ""; personality: str = ""

class ChildUpdateRequest(BaseModel):
    name: Optional[str] = None; avatar: Optional[str] = None; photo: Optional[str] = None
    relationship: Optional[str] = None; personality: Optional[str] = None

class TaskAckRequest(BaseModel):
    task_id: int

# ── In-memory task store ─────────────────────────────────
_next_task_id = 1
task_store: dict[int, dict] = {}
pushed_today: dict[int, date] = {}
played_history: list[dict] = []

SENSITIVE_PATTERNS = {
    "money": ["银行卡","密码","转账","汇款","账号","存折","现金","取钱"],
    "threat": ["不要你","滚开","不听话","别吃了","去死","废物","没用","不想活","活够"],
    "medical": ["停药","不用吃药","别去医院","这个药没用","私自停药"],
    "privacy": ["身份证","家庭住址","门牌号","手机验证码"],
}

# ── Helpers ──────────────────────────────────────────────
def _select_video(text: str) -> str:
    if any(kw in text for kw in ["药","吃药","服药"]): return "medication_reminder.mp4"
    if any(kw in text for kw in ["饭","吃"]): return "dinner_reminder.mp4"
    if any(kw in text for kw in ["睡","休息","晚"]): return "bedtime_reminder.mp4"
    if any(kw in text for kw in ["运动","康复","活动"]): return "exercise_reminder.mp4"
    if any(kw in text for kw in ["心情","难过","想","孤独"]): return "emotional_comfort.mp4"
    return "daily_greeting.mp4"

def _rewrite_to_caring(text: str) -> str:
    for key, val in {"吃药":"到吃药时间啦，先把药吃了，再喝点温水~","提醒":"温柔地提醒您","睡觉":"今天辛苦啦，早点休息，明天精神会更好~","吃饭":"该吃饭啦，今天的饭菜很香哦","运动":"康复时间到啦，我们慢慢活动一下~"}.items():
        if key in text: return val
    return random.choice([f"亲爱的，{text}，我们慢慢来，不着急~",f"温馨提示：{text}，我会一直陪着您~",f"{text}，要照顾好自己哦~"])

def _should_push(task: dict) -> bool:
    mode = task["mode"]; now = datetime.now()
    if mode == "immediate": return not task.get("pushed")
    if mode in ("scheduled","daily") and task.get("scheduled_time"):
        try:
            h,m = map(int,task["scheduled_time"].split(":"))
            if now >= now.replace(hour=h,minute=m,second=0) and not task.get("pushed"):
                if mode == "daily":
                    today = date.today()
                    return pushed_today.get(task["id"]) != today
                return True
        except: pass
    return False

def _user_row_to_dict(row) -> dict:
    return dict(id=row["id"],name=row["name"],role=row["role"],avatar=row["avatar"],
                age=row["age"],condition=row["condition"],
                traits=json.loads(row["traits"]) if isinstance(row["traits"],str) else row["traits"],
                created_at=row["created_at"])

# ── Auth ─────────────────────────────────────────────────
@app.post("/api/auth/login")
def auth_login(req: LoginRequest):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE name=? AND role=?", (req.name, req.role)).fetchone()
    conn.close()
    if not row or row["password"] != req.password:
        raise HTTPException(401, "用户名或密码错误")
    user = _user_row_to_dict(row)
    return {"success": True, "user": user}

@app.get("/api/auth/me")
def auth_me(user_id: int):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    if not row: raise HTTPException(404, "User not found")
    return _user_row_to_dict(row)

# ── User listing ─────────────────────────────────────────
@app.get("/api/users/elderly")
def list_elderly(q: str = ""):
    conn = get_db()
    if q.strip():
        pattern = f"%{q.strip()}%"
        rows = conn.execute(
            "SELECT * FROM users WHERE role='elderly' AND (name LIKE ? OR traits LIKE ?)",
            (pattern, pattern)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM users WHERE role='elderly'").fetchall()
    conn.close()
    return {"users": [_user_row_to_dict(r) for r in rows]}

@app.get("/api/users/caregivers")
def list_caregivers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users WHERE role='caregiver'").fetchall()
    conn.close()
    return {"users": [_user_row_to_dict(r) for r in rows]}

# ── Admin CRUD ───────────────────────────────────────────
@app.get("/api/admin/users")
def admin_list_users():
    conn = get_db()
    rows = conn.execute("SELECT * FROM users ORDER BY role, name").fetchall()
    conn.close()
    return {"users": [_user_row_to_dict(r) for r in rows]}

@app.post("/api/admin/users")
def admin_create_user(req: UserCreateRequest):
    conn = get_db()
    traits_json = json.dumps(req.traits, ensure_ascii=False)
    try:
        cur = conn.execute(
            "INSERT INTO users (name,password,role,avatar,age,condition,traits) VALUES (?,?,?,?,?,?,?)",
            (req.name,req.password,req.role,req.avatar,req.age,req.condition,traits_json)
        )
        conn.commit()
        user_id = cur.lastrowid
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        conn.close()
        return {"success": True, "user": _user_row_to_dict(row)}
    except Exception as e:
        conn.close()
        raise HTTPException(400, str(e))

@app.put("/api/admin/users/{user_id}")
def admin_update_user(user_id: int, req: UserUpdateRequest):
    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not existing: conn.close(); raise HTTPException(404, "User not found")

    updates = {}
    if req.name is not None: updates["name"] = req.name
    if req.password is not None: updates["password"] = req.password
    if req.avatar is not None: updates["avatar"] = req.avatar
    if req.age is not None: updates["age"] = req.age
    if req.condition is not None: updates["condition"] = req.condition
    if req.traits is not None: updates["traits"] = json.dumps(req.traits, ensure_ascii=False)

    if updates:
        sets = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE users SET {sets} WHERE id=?", (*updates.values(), user_id))
        conn.commit()

    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return {"success": True, "user": _user_row_to_dict(row)}

@app.delete("/api/admin/users/{user_id}")
def admin_delete_user(user_id: int):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ── Children CRUD ──────────────────────────────────────────
@app.get("/api/elderly/{elderly_id}/children")
def list_children(elderly_id: int):
    conn = get_db()
    rows = conn.execute("SELECT * FROM children WHERE elderly_id=? ORDER BY created_at", (elderly_id,)).fetchall()
    conn.close()
    return {"children": [dict(r) for r in rows]}

@app.post("/api/elderly/{elderly_id}/children")
def create_child(elderly_id: int, req: ChildCreateRequest):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO children (elderly_id,name,avatar,photo,relationship,personality) VALUES (?,?,?,?,?,?)",
        (elderly_id, req.name, req.avatar, req.photo, req.relationship, req.personality)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM children WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return {"success": True, "child": dict(row)}

@app.put("/api/children/{child_id}")
def update_child(child_id: int, req: ChildUpdateRequest):
    conn = get_db()
    existing = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not existing: conn.close(); raise HTTPException(404, "Child not found")
    updates = {k:v for k,v in {
        "name":req.name, "avatar":req.avatar, "photo":req.photo,
        "relationship":req.relationship, "personality":req.personality
    }.items() if v is not None}
    if updates:
        sets = ", ".join(f"{k}=?" for k in updates)
        conn.execute(f"UPDATE children SET {sets} WHERE id=?", (*updates.values(), child_id))
        conn.commit()
    row = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    conn.close()
    return {"success": True, "child": dict(row)}

@app.delete("/api/children/{child_id}")
def delete_child(child_id: int):
    conn = get_db()
    conn.execute("DELETE FROM children WHERE id=?", (child_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ── Lingya AI Review ───────────────────────────────────────
LINGYA_API_KEY = os.getenv("LINGYA_API_KEY") or os.getenv("LLM_API_KEY")
LINGYA_BASE_URL = os.getenv("LINGYA_BASE_URL") or "https://api.lingyaai.cn/v1"
LINGYA_MODEL = os.getenv("LINGYA_MODEL") or "doubao-seed-2-0-mini"

def _lingya_review_text(text: str, elderly_profile: str = "", child_name: str = "") -> tuple:
    """Use Lingya API to review text content. Returns (passed, issues[], suggestion)."""
    if not LINGYA_API_KEY:
        return None, [], "Lingya API not configured"
    try:
        from openai import OpenAI
        client = OpenAI(api_key=LINGYA_API_KEY, base_url=LINGYA_BASE_URL)
        review_prompt = f"""你是养老照护内容安全审查助手。请判断以下护工输入的照护内容是否适合播放给老人。

【安全红线 - 出现任一即判block】：
- 威胁、恐吓、辱骂、羞辱或情绪操控老人
- 诱导转账、索要银行卡、密码、验证码、身份证
- 引导老人扫码付款、购买保健品、投资理财或联系陌生人
- 擅自建议停药、换药、加量、减量或替代就医
- 出现隐私泄露（证件、病历、家庭住址等）

【护工输入的照护内容】
{text}

【老人画像】
{elderly_profile or "（无）"}

【执行数字人身份】
{child_name or "AI陪伴助手"}

请严格输出JSON，不要多余解释：
{{"passed": true/false, "issues": [], "suggestion": ""}}"""
        resp = client.chat.completions.create(
            model=LINGYA_MODEL,
            messages=[{"role":"user","content":review_prompt}],
            max_tokens=500, temperature=0.1
        )
        result = json.loads(resp.choices[0].message.content)
        return result["passed"], result.get("issues", []), result.get("suggestion", "")
    except Exception as e:
        print(f"[Lingya review error] {e}")
        return None, [], str(e)

# ── Upload ────────────────────────────────────────────────
UPLOAD_ALLOWED = {"image/jpeg","image/png","image/webp","image/gif","image/bmp",
                   "video/mp4","video/webm","video/avi","video/mov","video/quicktime"}

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in UPLOAD_ALLOWED:
        raise HTTPException(400, f"不支持的文件类型: {file.content_type}，仅支持图片/视频")
    ext = {"image/jpeg":".jpg","image/png":".png","image/webp":".webp","image/gif":".gif","image/bmp":".bmp",
           "video/mp4":".mp4","video/webm":".webm","video/avi":".avi","video/mov":".mov","video/quicktime":".mov"}.get(file.content_type, ".bin")
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000,9999)}{ext}"
    path = os.path.join(UPLOADS_DIR, filename)
    with open(path, "wb") as f:
        f.write(await file.read())
    return {"success": True, "url": f"/api/uploads/{filename}"}

# ── Task Management ──────────────────────────────────────
@app.get("/api/tasks")
def list_tasks():
    return {"tasks": sorted(task_store.values(), key=lambda t: t["created_at"], reverse=True)}

@app.post("/api/tasks")
def create_task(req: TaskCreateRequest):
    # 1. Keyword-based review (always runs)
    passed, level, kw_issues, _ = _review_content(req.content)
    if not passed:
        detail = "; ".join(kw_issues)
        print(f"\n  [REVIEW BLOCKED] keyword check failed: {detail}\n")
        raise HTTPException(400, f"内容不合法，已拦截：{detail}")

    # 2. LLM-based review (if Lingya API configured)
    elderly_profile = req.profile_text
    llm_passed, llm_issues, llm_suggestion = _lingya_review_text(
        req.content, elderly_profile, req.child_name or ""
    )
    if llm_passed is False:
        detail = "; ".join(llm_issues) or llm_suggestion
        print(f"\n  [REVIEW BLOCKED] LLM check failed: {detail}\n")
        raise HTTPException(400, f"内容不合法，已拦截：{detail}")
    if llm_passed is None and llm_issues:
        print(f"  [Lingya unavailable] {llm_issues[0]} — falling back to keyword review only")

    # 3. Create task
    global _next_task_id
    task_id = _next_task_id; _next_task_id += 1
    video = req.custom_video_url or f"/api/videos/{_select_video(req.content)}"
    rewritten = _rewrite_to_caring(req.content)

    # Personalize greeting if child is specified
    if req.child_name:
        rewritten = f"我是{req.child_name}，{rewritten}"

    print(f"\n{'='*60}\n  [TASK] #{task_id} created: {req.elderly_name} | child:{req.child_name or 'AI'}\n  content: {req.content}\n{'='*60}\n")
    task = {"id":task_id,"elderly_id":req.elderly_id,"elderly_name":req.elderly_name,
            "elderly_avatar":req.elderly_avatar,"content":req.content,"rewritten":rewritten,
            "profile_text":req.profile_text,"mode":req.mode,"scheduled_time":req.scheduled_time,
            "child_id":req.child_id,"child_name":req.child_name,
            "photo_url":req.photo_url,"child_photo_url":req.child_photo_url,
            "video_url":video,"duration_seconds":15,
            "video_mode":req.video_mode,
            "ai_signature":"AI 亲情陪伴助手，由家人授权创建",
            "created_at":datetime.now().isoformat(),"pushed":False,"pushed_at":None}
    task_store[task_id] = task
    return {"success": True, "task": task}

@app.get("/api/tasks/pending")
def pending_tasks(elderly_id: int = 1):
    ready = [t for t in task_store.values() if t["elderly_id"] == elderly_id and _should_push(t)]
    return {"pending": ready}

@app.post("/api/tasks/ack")
def ack_task(req: TaskAckRequest):
    task = task_store.get(req.task_id)
    if not task: raise HTTPException(404, "Task not found")
    task["pushed"] = True; task["pushed_at"] = datetime.now().isoformat()
    if task["mode"] == "daily": pushed_today[req.task_id] = date.today()
    played_history.append({"task_id":task["id"],"elderly_name":task["elderly_name"],
        "title":task["rewritten"],"video_url":task["video_url"],
        "duration_seconds":task["duration_seconds"],"played_at":datetime.now().isoformat()})
    return {"success": True}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    task_store.pop(task_id, None); pushed_today.pop(task_id, None)
    return {"success": True}

@app.get("/api/tasks/history")
def task_history(elderly_id: int = 1):
    return {"history": list(reversed(played_history))}

# ── Legacy endpoints ─────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "亲伴 AI API", "db": os.path.exists(DB_PATH)}

def _review_content(text: str) -> tuple:
    """Internal content review. Returns (passed, risk_level, issues, rewritten_text)."""
    issues = []; level = "safe"
    for cat, kws in SENSITIVE_PATTERNS.items():
        for kw in kws:
            if kw in text:
                issues.append(f"检测到{cat}类敏感内容：「{kw}」")
                level = {"money":"high","medical":"high","threat":"high"}.get(cat, "medium")
    if issues:
        return False, level, issues, None
    return True, "safe", [], _rewrite_to_caring(text)

@app.post("/api/review-content", response_model=ReviewResult)
def review_content(req: ReviewRequest):
    passed, level, issues, rewritten = _review_content(req.text)
    if not passed:
        return ReviewResult(passed=False, risk_level=level, issues=issues)
    return ReviewResult(passed=True, risk_level="safe", issues=[], rewritten_text=rewritten)

@app.post("/api/audio/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    stt_key = os.getenv("STT_API_KEY")

    if stt_key:
        # TODO: call real STT service based on STT_PROVIDER
        text = "[STT] "  # placeholder — real integration replaces this
    else:
        # Mock: simulate transcription for demo
        text = random.choice([
            "我感觉有点不舒服，能陪我说说话吗？",
            "这个药我不想吃了，太难吃了",
            "我想我的儿子了，他什么时候来看我？",
            "今天天气真好，我想出去走走",
            "我不想活了，活着没意思",
        ])

    safe, level, issues, rewritten = _review_content(text)
    return TranscribeResponse(text=text, safe=safe, issues=issues, rewritten_text=rewritten)

@app.post("/api/generate-care-reminder")
def generate_care_reminder(req: CareReminderRequest):
    video = _select_video(req.prompt)
    rewritten = _rewrite_to_caring(req.prompt)
    print(json.dumps({"api":"generate-care-reminder","profile_text":req.profile_text,"prompt":req.prompt,"rewritten":rewritten}, ensure_ascii=False))
    return {"success":True,"rewritten":rewritten,"video_url":f"/api/videos/{video}",
            "duration_seconds":15,"ai_signature":"AI 亲情陪伴助手，由家人授权创建",
            "task_id":f"task_{random.randint(1000,9999)}"}

@app.post("/api/generate-video")
def generate_video(req: VideoRequest):
    return {"success":True,"video_url":"/api/videos/medication_reminder.mp4","duration_seconds":15,
            "generation_time_ms":0,"ai_signature":"AI 亲情陪伴助手，由家人授权创建",
            "task_id":f"task_{random.randint(1000,9999)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
