"""
YOLO 모델 로드하고 관리하는 모듈
적절한 디바이스(CPU, GPU, MPS)에 모델을 로드
"""

import torch #PyTorch 임포트 (텐서 연산 및 GPU사용)
from ultralytics import YOLO # YOLO 모델 클래스

class ModelLoader:
    """ YOLO 모델을 로드하고 관리하는 클래스 """
    def __init__(self, model_path='./yolo8n.pt'): # 기본값
        self.model_path = model_path    # 모델 파일 경로
        self.device = self._get_device()    # 사용할 디바이스 결정
        self.model = None   # 모델 객체 (아직 로드되지 않음)

    def _get_device(self):
        """ 적절한 연산 디바이스 결정, 'mps' (Apple Silicon), 'cuda' (NVIDIA GPU) 또는 'cpu'"""
        return 'mps' if torch.backends.mps.is_available() else 'cpu'

    def load_model(self):
        """ YOLO 모델 로드 및 지정된 디바이스 이동"""
        print(f"Loading model on device: {self.device}")
        # YOLO 모델 로드
        self.model = YOLO(self.model_path)
        # 모델을 지정된 디바이스로 이동
        self.model.to(self.device)
        return self.model