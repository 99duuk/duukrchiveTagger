import os
import shutil
import time
from pathlib import Path

import cv2
from ultralytics import YOLO
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# M3 MPS 활용 - 디바이스 설정
import torch
device = 'mps' if torch.backends.mps.is_available() else 'cpu'
print(f"Using device: {device}")

# YOLO 모델 로드 (TODO 우선 기본 pretrained 모델 사용, 추후 커스텀)
model = YOLO('yolov8n.pt')
model.to(device)

# 감지할 기본 태그와 대분류 매핑
TAG_MAPPING = {
    'person': 'pedestrian',
    'bicycle': 'bicycle',
    'car': 'car',
    # 'jeans' : 'jeans',9
    # 'texts' : 'text',
    'shoes' : 'shoes',
    'book' : 'book',
    # 'webtoons' : 'webtoons'

}

# 기본 디렉터리 설정
BASE_DIR = Path.home() / "Desktop" / "duukrchive"
OUTPUT_BASE_DIR = BASE_DIR

def ensure_output_dir(tag):
    """태그에 맞는 출력 디렉터리 생성"""
    output_dir = OUTPUT_BASE_DIR / tag
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def analyze_image(image_path):
    """YOLO로 이미지 분석 후 태그 반환"""
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not load image {image_path}")
        return []

    # YOLO 예측
    results = model(img, conf=0.3, verbose=False)   # confidence threshold 0.3 이하의 신뢰도를 가진 탐지 결과는 무시, 높을수록 정확..

    detections = results[0].boxes

    tags = set()
    for detection in detections:
        label = model.names[int(detection.cls)]
        # TAG_MAPPING에 있는 객체만 태그로 추가
        if label in TAG_MAPPING:
            tags.add(TAG_MAPPING[label])

    return list(tags)


def classify_and_move(image_path):
    """이미지 분류 후 이동"""
    tags = analyze_image(image_path)
    if not tags:
        print(f"No recognized objects in {image_path}, skipping...")
        return

    # 첫 번째 태그를 대분류로 사용
    primary_tag = tags[0]
    print(f"Image {image_path} is classified as tags: {tags}, primary: {primary_tag}")

    # 파일 이동
    output_dir = ensure_output_dir(primary_tag)
    dest_path = output_dir / Path(image_path).name
    shutil.move(image_path, dest_path)
    print(f"Moved {image_path} to {dest_path}")


class ImageHandler(FileSystemEventHandler):
    """새 파일 감지 시 처리"""
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        # 이미지 파일만 처리 (확장자 필터링)
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            print(f"New image detected: {file_path}")
            # 파일이 완전히 쓰여질 떄까지 잠시 대기 (for 안정성)
            time.sleep(1)
            classify_and_move(file_path)


def start_watching():
    """디렉터리 감시 시작"""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, str(BASE_DIR), recursive=False)
    observer.start()
    print(f"Started watching {BASE_DIR}... ")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching()
