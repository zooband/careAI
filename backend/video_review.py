"""
亲伴 AI — 视频安全审查模块（灵崖AI）

视频安全审查模块，提取自原 test_lingya_video.py。
API密钥从项目根目录 .env 读取，不再硬编码。
"""
import os, json, base64
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

LINGYA_API_KEY = os.getenv("LINGYA_API_KEY")
LINGYA_BASE_URL = os.getenv("LINGYA_BASE_URL") or "https://api.lingyaai.cn/v1"
LINGYA_MODEL = os.getenv("LINGYA_MODEL") or "doubao-seed-2-0-mini"


def review_video(video_path: str, care_task: str, approved_script: str = "",
                 generation_prompt: str = "") -> dict:
    """
    审查一段AI照护视频是否适合播放给老人。

    参数:
        video_path:      本地视频文件路径
        care_task:       护工原始任务（如"提醒王奶奶晚上8点吃降压药"）
        approved_script: 审核通过的话术（可选）
        generation_prompt: 视频生成Prompt（可选）

    返回:
        {"final_decision": "pass|review|block",
         "video_summary": "...",
         "hard_fail_reasons": [...],
         "issues": [...],
         "suggestion": "..."}
    """
    if not LINGYA_API_KEY:
        return {
            "final_decision": "review",
            "video_summary": "",
            "hard_fail_reasons": ["Lingya API 未配置，无法自动审查"],
            "issues": [],
            "suggestion": "请配置 LINGYA_API_KEY 后重试，或人工复核。"
        }

    if not os.path.exists(video_path):
        return {
            "final_decision": "block",
            "video_summary": "",
            "hard_fail_reasons": [f"视频文件不存在: {video_path}"],
            "issues": [],
            "suggestion": "请检查视频路径是否正确。"
        }

    from openai import OpenAI
    client = OpenAI(api_key=LINGYA_API_KEY, base_url=LINGYA_BASE_URL)

    # Base64 编码视频
    file_size_mb = os.path.getsize(video_path) / 1024 / 1024
    if file_size_mb > 45:
        return {
            "final_decision": "review",
            "video_summary": "",
            "hard_fail_reasons": [f"视频文件太大 ({file_size_mb:.1f}MB)，建议使用公网URL"],
            "issues": [],
            "suggestion": "请压缩视频或上传到对象存储后使用URL。"
        }

    with open(video_path, "rb") as f:
        video_b64 = base64.b64encode(f.read()).decode("utf-8")
    video_data_url = f"data:video/mp4;base64,{video_b64}"

    prompt = f"""
你是养老照护视频安全审查助手。

请根据视频内容和生成前信息，判断这段AI照护视频是否适合播放给老人。

重要原则：
- 不要求视频内容与生成Prompt逐字一致，只判断核心照护任务、核心话术含义和安全边界是否一致。
- 如果视频生成Prompt、护工任务、审核通过话术之间存在轻微不一致，优先以【护工原始任务】和【审核通过的话术】为判断依据。
- 如果视频未能完成核心照护任务，或者表达了与照护任务相反的意思，应判为block。
- 如果你无法确认某项内容，例如听不清语音、看不清字幕，不要武断判block，应判review，并说明需要人工复核。
- 所有判断必须基于视频中实际看到或听到的内容，不要凭空推测。

【护工原始任务】
{care_task}

【审核通过的话术】
{approved_script or care_task}

【视频生成Prompt】
{generation_prompt or care_task}

请从以下五个维度审查：
1. 任务一致性
2. 表达方式
3. 诈骗与隐私风险
4. 医疗与照护边界
5. 播放体验

一票否决规则：威胁、诈骗、医疗越界、严重异常 → 直接block。

最终判定规则：
- 任一维度为block → final_decision=block
- 不确定/听不清/看不清 → review
- 全部通过 → pass

请严格输出JSON，不要多余解释：
{{
  "video_summary": "",
  "dimension_results": {{
    "task_consistency": {{"status": "pass/review/block", "reason": ""}},
    "expression": {{"status": "pass/review/block", "reason": ""}},
    "fraud_privacy_risk": {{"status": "pass/review/block", "reason": ""}},
    "medical_care_boundary": {{"status": "pass/review/block", "reason": ""}},
    "playback_experience": {{"status": "pass/review/block", "reason": ""}}
  }},
  "hard_fail_triggered": false,
  "hard_fail_reasons": [],
  "final_decision": "pass/review/block",
  "suggestion": ""
}}
"""

    try:
        resp = client.chat.completions.create(
            model=LINGYA_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "video_url", "video_url": {"url": video_data_url, "fps": 1}},
                    {"type": "text", "text": prompt}
                ]
            }],
            max_tokens=1200,
            temperature=0.1
        )
        result = json.loads(resp.choices[0].message.content)
        issues = []
        for dim, res in result.get("dimension_results", {}).items():
            if res.get("status") == "block":
                issues.append(f"[{dim}] {res.get('reason','')}")
        return {
            "final_decision": result.get("final_decision", "review"),
            "video_summary": result.get("video_summary", ""),
            "hard_fail_reasons": result.get("hard_fail_reasons", []),
            "issues": issues,
            "suggestion": result.get("suggestion", ""),
        }
    except Exception as e:
        return {
            "final_decision": "review",
            "video_summary": "",
            "hard_fail_reasons": [f"审查调用失败: {type(e).__name__}: {e}"],
            "issues": [],
            "suggestion": "LLM审查异常，请人工复核。"
        }


if __name__ == "__main__":
    # 命令行用法示例
    import sys
    video = sys.argv[1] if len(sys.argv) > 1 else ""
    task = sys.argv[2] if len(sys.argv) > 2 else "提醒王奶奶晚上8点吃降压药"
    if not video:
        print("用法: python video_review.py <视频路径> [护工任务]")
        sys.exit(1)
    result = review_video(video, task)
    print(json.dumps(result, ensure_ascii=False, indent=2))
