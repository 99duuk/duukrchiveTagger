"""
이미지 분석 및 태깅 담당 뮤듈
로드된 YOLO 모델을 사용하여 이미지에서 객체를 감지하고 태그 생성
"""
import cv2
from pathlib import Path
from models.model_loader import ModelLoader


class ImageTagger:
    """ 이미지 분석 및 태깅 수행하는 클래스 """

    def __init__(self, model_loader, tag_mapping):
        # 모델 로더로부터 모델 가져오기
        self.model = model_loader.load_model()
        # 욜로 클래스 -> 내부 태그 매핑 저장
        self.tag_mapping = tag_mapping  # tag_mapping: 매핑 사전

    def analyze_image(self, image_path):
        """이미지 분석 후 태그 반환"""
        # OpenCV로 이미지 로드
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return []

        # YOLO 모델로 객체 감지 수행
        # confidence threshold 0.3 (30%) 이하의 신뢰도를 가진 탐지 결과는 무시, 높을수록 정확..
        results = self.model(img, conf=0.3, verbose=False)  # verbose: 상세 출력 여부

        # 감지 결과에서 바운딩 박스 정보 추출
        detections = results[0].boxes

        # 감지된 객체를 태그로 변환 (중복 제거를 위해 set 사용)
        tags = set()
        for detection in detections:
            # 클래스 ID를 클래스 이름으로 변환
            label = self.model.names[int(detection.cls)]
            # 태그 매핑에 있는 클래스만 태그로 추가
            if label in self.tag_mapping:
                tags.add(self.tag_mapping[label])

        # set을 list로 변환하여반환
        return list(tags)