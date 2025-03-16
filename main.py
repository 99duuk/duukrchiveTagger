"""
어플리케이션 시작점
각 컴포넌트를 초기화하고 실행 흐름 제어
"""

from interface.directory_watcher import DirectoryWatcher
from interface.kafka_producer import TagProducer
from models.model_loader import ModelLoader
from core.tagger import ImageTagger
from core.file_manager import FileManager
from config import Config

# 전역 변수 선언
tagger = None
file_manager = None
kafka_producer = None

def process_image(image_path):
    """
    새 이미지 파일 처리
    이 함수는 DirectoryWatcher에 의해 호출됨

    image_path (str): 처리할 이미지 파일 경로
    """
    print(f"Processing: {image_path}")
    try:
        # 1. 이미지 분석
        primary_tag, tags = tagger.analyze_image(image_path)

        # 태그가 없으면 처리 중단
        if not primary_tag:
            print(f"No recognized objects in {image_path}, skipping...")
            return

        print(f"Image {image_path} classified - Primary tag: {primary_tag}, Tags: {tags}")


        # 2. 파일 이동
        new_path = file_manager.move_file(image_path, primary_tag)
        print(f"Moved to: {new_path}")

        # 3. Kafka로 태그 정보 전송
        # kafka_producer.send_tag_data(new_path, tags, primary_tag)

    except Exception as e:
        print(f"이미지 처리 오류: {e}")




def main():
    """
    어플리케이션 메인 함수
    컴포넌트 초기화 및 디렉터리 감시 시작
    """
    # 설정 로드
    config = Config()
    try:
        # 모델 로더 초기화
        model_loader = ModelLoader(config.model_path)

        # 전역 변수로 선언한 컴포넌트들 초기화
        global  tagger, file_manager, kafka_producer

        # 태거 초기화 (모델 로더 및 태그 매핑 전달)
        tagger = ImageTagger(model_loader, config.tag_mapping, config.color_ranges)
        # 파일 관리자 초기화 (출력 디렉터리 전달)
        file_manager = FileManager(config.output_dir)
        # Kafka 프로듀서 초기화 (서버 주소 및 토픽 이름 전달)
        kafka_producer = TagProducer(config.kafka_bootstrap_servers, config.kafka_topic_name)


        # 디렉터리 감시 시작
        watcher = DirectoryWatcher(config.input_dir)
        # process_image 함수를 이벤트 콜백으로 등록
        watcher.start(process_image)
        print("디렉터리 감시 시작")
    except Exception as e:
        print(f"초기화 오류: {e}")
        return

    try:
        # 메인 스레드 계속 실행 유지
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Ctrl+C로 프로그램 종료 시 디렉터리 감시도 중지
        print("프로그램 종료 중...")
        watcher.stop()
        print("디렉터리 감시 중지됨.")


if __name__ == "__main__":
    main()
