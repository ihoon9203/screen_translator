class OCRText:
    def __init__(self, text: str, bbox: list, confidence: float):
        self.text = text              # 인식된 텍스트
        self.bbox = bbox              # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] 형태
        self.confidence = confidence  # 신뢰도
    
    def __repr__(self):
        return f"OCRText(text='{self.text}', bbox={self.bbox}, confidence={self.confidence})"