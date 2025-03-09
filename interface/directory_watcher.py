"""
디렉터리 감시 로직을 담당하는 모듈
watchdog 라이브러리 사용해 특정 디렉터리의 파일 변경 이벤트를 감지
"""
import time
from pathlib import Path

from watchdog.events import FileSystemEventHandler  # 디렉터리 변경 감시자
from watchdog.observers import Observer     # 파일 시스템 이벤트 처리기


class ImageEventHandler(FileSystemEventHandler):
    """
    파일 시스템 이벤트를 처리하는 핸들러 클래스
    특정 이벤트(파일 생성)가 발생하면 등록된 콜백 함수를 호출
    """
    def __init__(self, callback):
        """
        생성자: 콜백 함수를 저장
        callback(function): 새 파일 감지 시 호출할 함수
        """
        print("ImageEventHandler 초기화됨")
        self.callback = callback

    def on_created(self, event):
        """
        파일 생성 이벤트 처리 메서드
        event: watchdog 이벤트 객체 (생성된 파일 정보 포함)
        """
        print(f"이벤트 발생: {event.src_path}")  # 모든 생성 이벤트 로깅
        # 디렉터리인 경우 무시
        if  event.is_directory:
            return
        # 콜백 함수 호출하여 파일 처리 시작
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'}:
            print(f"새 이미지 감지: {file_path}")
            time.sleep(1)  # 파일 쓰기 완료 대기
            self.callback(str(file_path))


class DirectoryWatcher:
    """
    디렉터리 감시를 관리하는 클래스
    Observer를 실행하고 종료하는 메서드 제공
    """
    def __init__(self, directory_path):
        """
        생성자: 감시할 디렉터리 경로 저장
        directory_path(str): 감시할 디렉터리 경로
        """
        self.directory_path = directory_path
        self.observer = None
        print(f"감시 대상 디렉터리: {self.directory_path}")

    def process_existing_files(self, callback_function):
        """
        프로그램 시작 시 디렉터리 내 기존 파일을 처리
        callback_function(function): 파일 처리 시 호출할 함수
        """
        dir_path = Path(self.directory_path)
        print(f"기존 파일 확인 시작: {dir_path}")
        for file_path in dir_path.glob("*"):  # 모든 파일 검색
            if (file_path.is_file() and
                    file_path.suffix.lower() in {'.jpg', '.jpeg', '.png'} and
                    file_path.parent == dir_path):  # 최상위 디렉터리만
                print(f"기존 파일 감지: {file_path}")
                try:
                    callback_function(str(file_path))
                except Exception as e:
                    print(f"기존 파일 처리 오류: {e}")

    def start(self, callback_function):
        """
        디렉터리 감시 시작
        callback_function(function): 파일 생성 시 호출할 함수
        """
        # 기존 파일 먼저 처리
        self.process_existing_files(callback_function)

        # 이벤트 핸들러 생성 (콜백 함수 전달)
        event_handler = ImageEventHandler(callback_function)
        # Observer 객체 생성
        self.observer = Observer()
        # Observer에 감시할 디렉터리와 이벤트 핸들러 등록
        self.observer.schedule(event_handler, self.directory_path, recursive=False)
        # 감시 시작
        self.observer.start()
        print("Observer 시작됨")

    def stop(self):
        """ 디렉터리 감시 중지 """
        if self.observer:
            # 중지
            self.observer.stop()
            # Observer 스레드가 완전히 종료될 때까지 대기
            self.observer.join()