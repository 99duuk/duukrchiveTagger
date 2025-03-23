import hashlib

import requests


class HashUtil:
    """ 이미지 해시 관리 유틸리티 클래스 """
    def __init__(self, es_url):
        self.es_url = es_url
        self.processed_hashes = set()

    def load_hashes_from_es(self):
        """ es에서 기존 처리된 해시 로드 """
        try:
            responses = requests.get(f"{self.es_url}/image_hashes/_search?pretty", json={
                "query": {"match_all": {}},
                "fields": ["hash"],
                "_source": False,
                "size": 1000,
            })
            if responses.status_code == 200:
                hits = responses.json()["hits"]["hits"]
                self.processed_hashes = {hit["fields"]["hash"][0] for hit in hits}
                print(f"Loaded {len(self.processed_hashes)} hashes from {self.es_url}")
                return self.processed_hashes
            elif responses.status_code == 404:
                self.create_hashes_index()
                return self.processed_hashes
            else:
                print(f"Error loading hashes from ES: {responses.text}")
                return self.processed_hashes
        except Exception as e:
            print(f"Failed to connect to ES: {e}")
            return self.processed_hashes


    def create_hashes_index(self):
        """ ES에 image_hashes 인덱스 생성 """
        mapping = {
            "mappings": {
                "properties": {
                    "hash" : {"type": "keyword"},
                }
            }
        }
        responses = requests.put(f"{self.es_url}/image_hashes", json=mapping)
        if responses.status_code not in (200, 201):
            print(f"Failed to create image_hashes index: {responses.text}")

    def save_hash_to_es(self, img_hash):
        """ ES에 새 해시 저장 """
        if img_hash not in self.processed_hashes:
            doc = {"hash": img_hash}
            response = requests.post(f"{self.es_url}/image_hashes/_doc", json=doc)
            if response.status_code in (200, 201):
                self.processed_hashes.add(img_hash)
                print(f"Saved hash: {img_hash}")
            else:
                print(f"Failed to save hash to ES: {response.text}")

    def get_image_hash(self, image_path):
        """ 이미지의 SHA256 해시 계산 """
        with open(image_path, 'rb') as f:
            img_bytes = f.read()
            return hashlib.sha256(img_bytes).hexdigest()

    def is_duplicate(self, image_path):
        """ 중복 이미지 체크 """
        img_hash = self.get_image_hash(image_path)
        return img_hash in self.processed_hashes

