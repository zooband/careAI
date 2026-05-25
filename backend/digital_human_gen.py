"""
亲伴 AI — 数字人视频生成模块（OpenAI Sora API）

输入数字人图片、prompt，输出一段数字人视频（不可交互）。
API密钥从 .env 读取 OPENAI_API_KEY。
"""
import os, time
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))


def generate_digital_human_video(
    image_path: str,
    prompt: str,
    output_path: str = "",
    size: str = "1280x720",
    seconds: str = "8",
) -> str:
    """
    生成数字人视频。

    参数:
        image_path: 数字人图片路径
        prompt:     视频生成 prompt
        output_path: 输出视频路径（默认自动生成）
        size:       视频尺寸，默认 1280x720
        seconds:    视频时长（秒），默认 8

    返回:
        生成的视频文件路径

    异常:
        ValueError: OPENAI_API_KEY 未配置
        RuntimeError: 视频生成失败
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 未配置，请在 .env 中设置")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    with open(image_path, "rb") as f:
        video = client.videos.create(
            model="sora-2-pro",
            prompt=prompt,
            size=size,
            seconds=seconds,
            input_reference=f,
        )

    while video.status not in ("completed", "failed"):
        time.sleep(5)
        video = client.videos.retrieve(video.id)

    if video.status == "failed":
        raise RuntimeError(f"视频生成失败: {video}")

    if not output_path:
        output_path = f"output_{video.id}.mp4"

    content = client.videos.download_content(video.id, variant="video")
    content.write_to_file(output_path)

    return output_path


if __name__ == "__main__":
    import sys
    image = sys.argv[1] if len(sys.argv) > 1 else "image_1280x720.png"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "She turns around and smiles, then slowly walks out of the frame."
    output = generate_digital_human_video(image, prompt)
    print(output)
