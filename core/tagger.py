"""
이미지 분석 및 태깅 담당 뮤듈
로드된 YOLO 모델을 사용하여 이미지에서 객체를 감지하고 태그 생성
"""
import cv2
import numpy as np
from torch.utils.hipify.hipify_python import mapping


class ImageTagger:
    """ 이미지 분석 및 태깅 수행하는 클래스 """
    def __init__(self, model_loader, tag_mapping, color_ranges):
        # 모델 로더로부터 모델 가져오기
        self.model = model_loader.load_model()  # YOLO 모델 로드 추가

        # 태그 사전을 외부에서 주입받음 (Config에서 로드된 데이터)
        self.tag_mapping = tag_mapping  # 태그 매핑

        # 색상 사전을 외부에서 주입받음 (Config에서 로드된 데이터)
        self.color_ranges = color_ranges  # 색상 범위

    def analyze_color(self, img, box):
        """ 바운딩 박스 내 주요 색상 분석 """
        # 바운딩 박스 좌표 추출 (x1, y1, x2, y2) - YOLO xyxy 순서에 맞게 수정
        x1, y1, x2, y2 = map(int, box.xyxy[0])  # [x_min, y_min, x_max, y_max]

        # 좌표 유효성 검사 및 조정
        h, w = img.shape[:2]  # 이미지 높이와 너비
        x1 = max(0, x1)  # 음수 방지
        y1 = max(0, y1)
        x2 = min(w, x2)  # 이미지 크기 초과 방지
        y2 = min(h, y2)

        # 슬라이싱 전에 크기 확인
        if x1 >= x2 or y1 >= y2:
            print(f"Invalid bounding box: ({x1}, {y1}, {x2}, {y2}) - skipping color analysis")
            return []

        roi = img[y1:y2, x1:x2]  # 바운딩 박스 영역 추출
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)  # BGR to HSV 변환

        colors = []  # 감지된 색상 저장
        for color_name, range_data in self.color_ranges.items():
            lower = np.array(range_data["lower"])  # 하한값
            upper = np.array(range_data["upper"])  # 상한값
            mask = cv2.inRange(hsv, lower, upper)  # 범위 내 픽셀 마스크
            if cv2.countNonZero(mask) > (roi.size * 0.1):  # 10% 이상이면 색상 추가
                colors.append(color_name)
        return colors

    def analyze_image(self, image_path):
        """이미지 분석 후 대분류 태그와 나머지 태그 반환"""
        # OpenCV로 이미지 로드
        img = cv2.imread(str(image_path))
        if img is None:
            print(f"Error: Could not load image {image_path}")
            return []

        # YOLO 모델로 객체 감지 수행
        results = self.model(img, conf=0.25, verbose=False)   # verbose: 상세 출력 여부
        detections = results[0].boxes   # 감지 결과에서 바운딩 박스 정보 추출

        # 감지 결과 로깅
        if len(detections) == 0:
            print(f"=================================================================")
            print(f"No objects detected in {image_path} (confidence threshold: 0.25)")
            return None, []

        # confidence 순으로 객체 정렬
        detected_objects = []
        for detection in detections:
            label = self.model.names[int(detection.cls)]  # 클래스 이름
            confidence = float(detection.conf)  # 신뢰도
            if label in self.tag_mapping and confidence >= 0.25:
                detected_objects.append((label, confidence, detection))

        # confidence 기준 내림차순 정렬
        detected_objects.sort(key=lambda x: x[1], reverse=True)

        # 대분류: 가장 높은 confidence를 가진 객체
        primary_tag = None
        if detected_objects:
            primary_label = detected_objects[0][0]
            primary_tag = self.tag_mapping[primary_label]["category"]
            print(f"Primary tag (highest confidence): {primary_tag}")

        # 나머지 태그 생성
        tags = set()
        for label, confidence, section in detected_objects:
            mapping = self.tag_mapping[label]
            tags.add(mapping["category"]) # 대분류 추가
            tags.add(mapping["subcategory"]) # 소분류 추가

            # 색상 분석
            colors = self.analyze_color(img, detection)
            tags.update(colors)

        # 대분류는 태그 목록에서 제외 (중복 방지)
        if primary_tag in tags:
            tags.remove(primary_tag)

        return primary_tag, list(tags) # 대분류와 나머지 태그 반환