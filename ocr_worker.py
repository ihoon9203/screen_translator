import io
import os
from google.cloud import vision
from dotenv import load_dotenv

class OCRWorker: 
    def __init__(self, language_list):
        self.language_list = language_list  # 언어 리스트 저장
        load_dotenv('key.env')
        self.key = os.getenv("CLOUD_LOCAL_KEY")
        self.client = vision.ImageAnnotatorClient()
        self.client.credentials = self.key

    def change_language(self, language_list):
        self.reader.setLanguageList(language_list)

    def process_image(self, image_path):
        try:
            # 로컬 파일을 읽어서 Vision API에 전달
            with io.open(image_path, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)

            # 텍스트 감지 수행
            print(self.language_list)
            response = self.client.text_detection(
                image=image,
                image_context=vision.ImageContext(
                    language_hints=self.language_list
                )
            )
            texts = response.text_annotations

            if response.error.message:
                raise Exception(f'{response.error.message}')

            # EasyOCR 형식으로 변환 [(bbox, text, confidence), ...]
            results = []
            
            if texts:
                # 첫 번째는 전체 텍스트, 나머지는 개별 단어/구문
                for i, text in enumerate(texts[1:], 1):  # 첫 번째(전체) 제외
                    # 바운딩 박스 좌표 추출
                    vertices = text.bounding_poly.vertices
                    bbox = [[vertex.x, vertex.y] for vertex in vertices]
                    
                    # 텍스트 내용
                    detected_text = text.description
                    
                    # 신뢰도 (Vision API는 신뢰도를 제공하지 않으므로 기본값 사용)
                    confidence = 0.95  # Vision API는 일반적으로 높은 정확도
                    
                    results.append((bbox, detected_text, confidence))
            
            return results
            
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return []


if __name__ == "__main__":
    worker = OCRWorker(['ko', 'en'])
    result = worker.process_image('example.jpg')
    print(result)