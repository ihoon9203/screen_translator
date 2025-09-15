import easyocr

class OCRWorker: 
    def __init__(self, language_list):
        self.language_list = language_list  # 언어 리스트 저장
        self.reader = easyocr.Reader(language_list)

    def change_language(self, language_list):
        self.reader.setLanguageList(language_list)

    def process_image(self, image_path):
        result = self.reader.readtext(image_path)
        return result


if __name__ == "__main__":
    worker = OCRWorker(['ko', 'en'])
    worker.change_language(['ko', 'en'])
    result = worker.process_image('example.jpg')
    print(result)