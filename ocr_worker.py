import io
import os
from google.cloud import vision
from dotenv import load_dotenv

from ocr_text import OCRText

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
            results = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        paragraph_text = ""
                        paragraph_bbox = [[v.x, v.y] for v in paragraph.bounding_box.vertices]

                        for word in paragraph.words:
                            word_text = "".join([s.text for s in word.symbols])
                            paragraph_text += word_text + " "

                        paragraph_text = paragraph_text.strip()
                        confidence = 0.95  # Vision API는 paragraph 단위 confidence 제공 X

                        if paragraph_text:
                            results.append(OCRText(paragraph_text, paragraph_bbox, confidence))
            print(results)
            return results
            
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            return []


if __name__ == "__main__":
    worker = OCRWorker(['ko', 'en'])
    result = worker.process_image('example.jpg')
    print(result)