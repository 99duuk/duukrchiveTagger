"""
파일 이동/관리 로직
태그에 따른 디렉터리 생성 및 파일 이동
"""
import shutil # 파일 이동 기능
from pathlib import Path # 경로 처리용 라이브러리



class FileManager:
    """ 태그 기반 파일 관리 기능을 제공하는 클래스 """
    def __init__(self, base_output_dir):
        """ 생성자: 기본 출력 디렉터리 저장"""
        # 문자열 경로를 Path 객체로 변환 (크로스 플랫폼 경로 처리 용이)
        self.base_output_dir = Path(base_output_dir)


    def ensure_output_dir(self, tag):
        """
        태그에 맞는 출력 디렉터리 생성
        tag (str): 파일 분류 태그
        Path: 생성된 디렉터리 경로 객체
        """
        # 기본 디렉터리 아래에 태그 이름의 서브 디렉터리 경로 생성
        output_dir = self.base_output_dir / tag
        # 디렉터리가 없으면 생성 (부모 디렉터리도 함께)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def move_file(self, file_path, tag):
        """
        파일을 해당 태그 디렉터리로 이동
        file_path (str): 이동할 파일 경로
        tag (str): 대상 태그 디렉터리
        returns: str: 이동할 파일의 새 경로
        """
        # 태그 디렉터리 확인/생성
        output_dir = self.ensure_output_dir(tag)
        # 대상 파일의 새 경로 (원본 파일명 유지)
        dest_path = output_dir / Path(file_path).name
        # 파일 이동
        shutil.move(file_path, dest_path)
        # 새 경로 문자열 반환
        return str(dest_path)