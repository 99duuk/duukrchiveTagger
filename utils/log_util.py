# """로깅 관련 유틸"""
# def print_progress(video_id, frame_seq, total_frames):
#     """진행 상황을 한 줄에서 퍼센트와 진행 바로 업데이트"""
#     progress = (frame_seq / total_frames) * 100
#     bar_length = 30  # 진행 바 길이
#     filled_length = int(bar_length * frame_seq // total_frames)
#     bar = "#" * filled_length + " " * (bar_length - filled_length)
#     # \r로 한 줄에서 업데이트
#     print(f"\r==> Processing {video_id}... {bar} {progress:.1f}%", end="", flush=True)