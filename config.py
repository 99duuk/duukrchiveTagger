"""설정 관리"""
import json
from pathlib import Path

class Config:
    """
    어플리케이션 설정을 관리하는 클래스
    모든 설정 값을 중앙에서 관리
    """

    def __init__(self):
        """
        생성자: 기본 설정값 초기화
        환경 변수나 설정 파일에서 값을 로드하도록 확장 가능
        """
        # 기본 디렉터리 설정
        # ~ (틸드)는 사용자 홈 디렉터리를 의미
        self.base_dir = Path.home() / "Desktop" / "duukrchive"
        # 입력 디렉터리 (새 파일 감시)
        self.input_dir = self.base_dir
        # 출력 디렉터리 (분류된 파일 저장)
        self.output_dir = self.base_dir

        # 모델 설정
        # yolo8n.pt는 YOLOv8 Nano 모델 (가장 작고 빠른 버전)
        self.model_path = "./models/yolov8n.pt"

        # Kafka 설정
        self.kafka_bootstrap_servers = ["localhost:9092"]     # Kafka 브로커 주소
        self.kafka_topic_name = "image_tags"     # 태그 데이터를 발행할 토픽

        # 태그 매핑 (YOLO 클래스 이름 -> 내부 태그)
        self.tag_mapping_file = "tags.json"
        self.colors_file = "colors.json"

        # 태그 매핑 로드
        try:
            with open(self.tag_mapping_file, 'r') as f:
                self.tag_mapping = json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.tag_mapping_file} not found. Using empty mapping.")
            self.tag_mapping = {}
        except json.JSONDecodeError:
            print(f"Error: {self.tag_mapping_file} is invalid JSON. Using empty mapping.")
            self.tag_mapping = {}

        # 색상 매핑 로드
        try:
            with open(self.colors_file, 'r') as f:
                self.color_ranges = json.load(f)
        except FileNotFoundError:
            print(f"Error: {self.colors_file} not found. Using empty ranges.")
            self.color_ranges = {}
        except json.JSONDecodeError:
            print(f"Error: {self.colors_file} is invalid JSON. Using empty ranges.")
            self.color_ranges = {}