"""
Kafka로 메시지 발행 기능 담당 모듈
태깅된 이미지 정보를 Kafka 토픽으로 전송
"""

from kafka import KafkaProducer # Kafka 프로튜서 클래스
import json

class TagProducer:
    """
    Kafka로 태그 데이터 발행하는 클래스
    """
    def __init__(self, bootstrap_servers, topic_name):
        """
        생성자: Kafka 프로듀서 초기화
        bootstrap_servers (list): Kafka 서버 주소 목록
        topic_name (str): 토픽 이름
        """
        # Kafka 프로듀서 객체 생성
        # value_serializer: Python 객체를 바이트로 직렬화하는 함수 지정 (JSON 형식)
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode('utf-8') # Python 객체 -> JSON -> UTF-8
        )
        self.topic_name = topic_name


    def _get_timestamp(self):
        """ 현재 시간을 ISO 형식 문자열로 반환 """
        from datetime import datetime
        return datetime.now().isoformat() # ex: 2025-03-10T15:30:45.123456

    def send_tag_data(self, file_path, tags, primary_tag):
        """
        태그 데이터를 kafka 토픽으로 전송
        file_path (str): 이동된 파일 경로
        tags (list): 나머지 태그 목록
        primary_tag (str): 대분류 태그
        """
        try:
            # 전송할 메시지 구조
            message = {
                "file_path": file_path,
                "primary_tag": primary_tag,
                "tags" : tags,
                "timestamp": self._get_timestamp(),
            }
            # Kafka 토픽으로 메시지 발행
            self.producer.send(self.topic_name, value=message)
            self.producer.flush()   # 즉시 전송 보장 (비동기 처리 시 제거 가능)
            print(f"Sent to Kafka topic: '{self.topic_name}' : {message}")
        except Exception as e:
            print(f"Error sending to Kafka: {e}")


    def close(self):
        """ Kafka Producer 종료 """
        self.producer.close()
        print("Kafka Producer closed")