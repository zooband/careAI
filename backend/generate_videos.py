"""Generate test videos for the qinban AI demo using ffmpeg."""
import subprocess
import os

VIDEOS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)

def make_video(filename, bg_color, text, duration=12, text_color="white", font_size=36):
    path = os.path.join(VIDEOS_DIR, filename)
    # Create a video with colored background, centered text, and a subtle animation effect
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
        "-vf", (
            f"drawtext=text='{text}':fontcolor={text_color}:fontsize={font_size}:"
            f"x=(w-text_w)/2:y=(h-text_h)/2:"
            f"enable='between(t,0,{duration})':"
            f"shadowcolor=black@0.4:shadowx=4:shadowy=4,"
            f"drawtext=text='AI\xe4\xba\xb2\xe6\x83\x85\xe9\x99\xaa\xe4\xbc\xb4\xe5\x8a\xa9\xe6\x89\x8b':"
            f"fontcolor=white@0.6:fontsize=16:x=w-text_w-20:y=h-text_h-40:"
            f"enable='between(t,0,{duration})',"
            f"fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1"
        ),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  OK: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"  FAIL: {filename}\n  {e.stderr}")

def video_with_text_animation(filename, bg_color, lines, duration=15):
    """Create a video with scrolling/multi-line text animation."""
    path = os.path.join(VIDEOS_DIR, filename)
    # Build complex drawtext filter for each line
    filters = []
    total_lines = len(lines)
    line_height = 80
    start_y = (1920 - (total_lines * line_height)) // 2

    for i, (text, color, size) in enumerate(lines):
        y_pos = start_y + i * line_height
        filters.append(
            f"drawtext=text='{text}':fontcolor={color}:fontsize={size}:"
            f"x=(w-text_w)/2:y={y_pos}:"
            f"enable='between(t,0,{duration})':"
            f"shadowcolor=black@0.3:shadowx=3:shadowy=3"
        )

    all_filters = ",".join(filters)
    # Add fade in/out
    all_filters += f",fade=t=in:st=0:d=1,fade=t=out:st={duration-1}:d=1"

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
        "-vf", all_filters,
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  OK: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"  FAIL: {filename}\n  {e.stderr}")

def video_with_watermark(filename, bg_color, main_text, duration=12):
    """Create video with main text and watermark banner."""
    path = os.path.join(VIDEOS_DIR, filename)

    # Use a single drawtext with more complex styling
    # For Chinese text we need a font that supports it
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c={bg_color}:s=1080x1920:d={duration}",
        "-vf", (
            f"drawtext=text='{main_text}':fontcolor=white:fontsize=42:"
            f"x=(w-text_w)/2:y=(h-text_h)/2-40:"
            f"enable='between(t,0,{duration})':"
            f"shadowcolor=black@0.5:shadowx=4:shadowy=4,"
            f"drawtext=text='\xe2\x99\xa5 \xe4\xba\xb2\xe4\xbc\xb4 AI \xe2\x99\xa5':fontcolor=#FFD700:fontsize=24:"
            f"x=(w-text_w)/2:y=(h-text_h)/2+60:"
            f"enable='between(t,0,{duration})':"
            f"shadowcolor=black@0.3:shadowx=2:shadowy=2,"
            f"drawtext=text='AI \xe4\xba\xb2\xe6\x83\x85\xe9\x99\xaa\xe4\xbc\xb4\xe5\x8a\xa9\xe6\x89\x8b':"
            f"fontcolor=white@0.5:fontsize=18:x=w-text_w-30:y=h-text_h-50:"
            f"enable='between(t,0,{duration})',"
            f"fade=t=in:st=0:d=1.5,fade=t=out:st={duration-1.5}:d=1.5"
        ),
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-pix_fmt", "yuv420p",
        path
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  OK: {filename}")
    except subprocess.CalledProcessError as e:
        print(f"  FAIL: {filename}\n  {e.stderr}")

if __name__ == "__main__":
    print("Generating demo videos...")

    print("1. Medication reminder (Alzheimer's scenario)")
    # Warm tone - medication reminder
    video_with_watermark(
        "medication_reminder.mp4",
        bg_color="0x6B4E8A",  # Deep purple
        main_text="奶奶，到吃药时间啦~\n先把降压药吃了\n再喝点温水哦",
        duration=15
    )

    print("2. Check-in greeting")
    video_with_watermark(
        "daily_greeting.mp4",
        bg_color="0x4A7C6F",  # Soft teal green
        main_text="奶奶，今天感觉怎么样？\n记得多活动活动身体~",
        duration=12
    )

    print("3. Exercise reminder")
    video_with_watermark(
        "exercise_reminder.mp4",
        bg_color="0x8B5E3C",  # Warm brown
        main_text="下午的康复时间到啦\n我们慢慢来活动一下~",
        duration=12
    )

    print("4. Dinner reminder")
    video_with_watermark(
        "dinner_reminder.mp4",
        bg_color="0xC0784E",  # Warm orange
        main_text="奶奶，该吃晚饭了\n今天的饭菜很香哦",
        duration=10
    )

    print("5. Bedtime reminder")
    video_with_watermark(
        "bedtime_reminder.mp4",
        bg_color="0x3D5A80",  # Deep blue
        main_text="时间不早啦，今天辛苦了\n我们早点休息吧~",
        duration=12
    )

    print("6. Emotional comfort")
    video_with_watermark(
        "emotional_comfort.mp4",
        bg_color="0x7C5C8B",  # Muted purple
        main_text="妈，我知道您想家里人了\n孩子一直惦记着您呢",
        duration=15
    )

    print("\nAll videos generated!")
