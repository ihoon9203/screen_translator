from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QTextEdit, QSplitter
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PIL import Image, ImageDraw, ImageFont
import os


class ImageViewer(QMainWindow):
    """OCR 결과를 시각적으로 표시하는 이미지 뷰어"""
    
    def __init__(self, image_path, ocr_results):
        super().__init__()
        self.image_path = image_path
        self.ocr_results = ocr_results
        self.current_image = None
        
        self.setWindowTitle("OCR 결과 뷰어")
        self.setGeometry(100, 100, 1200, 800)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃 (수평 분할)
        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 왼쪽: 이미지 영역
        self.setup_image_area(splitter)
        
        # 오른쪽: 텍스트 결과 영역
        self.setup_text_area(splitter)
        
        # 분할 비율 설정
        splitter.setSizes([800, 400])
        
        # 이미지 로드 및 표시
        self.load_and_display_image()
    
    def setup_image_area(self, parent):
        """이미지 표시 영역 설정"""
        image_widget = QWidget()
        image_layout = QVBoxLayout(image_widget)
        
        # 스크롤 영역
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 이미지 라벨
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        self.scroll_area.setWidget(self.image_label)
        
        image_layout.addWidget(self.scroll_area)
        parent.addWidget(image_widget)
    
    def setup_text_area(self, parent):
        """텍스트 결과 영역 설정"""
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        # 제목
        title_label = QLabel("OCR 결과")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        text_layout.addWidget(title_label)
        
        # 텍스트 결과 표시
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
                background-color: #f8f8f8;
                border: 1px solid #ddd;
            }
        """)
        text_layout.addWidget(self.text_display)
        
        # 버튼들
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("텍스트 저장")
        self.save_button.clicked.connect(self.save_text)
        button_layout.addWidget(self.save_button)
        
        self.close_button = QPushButton("닫기")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        text_layout.addLayout(button_layout)
        parent.addWidget(text_widget)
    
    def load_and_display_image(self):
        """이미지 로드 및 OCR 결과와 함께 표시"""
        try:
            # PIL로 이미지 로드
            pil_image = Image.open(self.image_path)
            self.current_image = pil_image.copy()
            
            # OCR 결과를 이미지에 그리기
            self.draw_ocr_results(pil_image)
            
            # PIL 이미지를 QPixmap으로 변환
            pil_image.save("temp_ocr_result.jpg", "JPEG")
            pixmap = QPixmap("temp_ocr_result.jpg")
            
            # 이미지 크기에 맞게 라벨 크기 조정
            self.image_label.setPixmap(pixmap)
            self.image_label.setMinimumSize(pixmap.size())
            
            # 텍스트 결과 표시
            self.display_text_results()
            
            # 임시 파일 삭제
            if os.path.exists("temp_ocr_result.jpg"):
                os.remove("temp_ocr_result.jpg")
                
        except Exception as e:
            print(f"이미지 로드 오류: {e}")
    
    def draw_ocr_results(self, image):
        """OCR 결과를 하얀색 배경에 검은색 글자로 덮어씌우기"""
        draw = ImageDraw.Draw(image)
        
        for i, (bbox, text, confidence) in enumerate(self.ocr_results):
            # 바운딩 박스의 중심점 계산
            center_x = sum(point[0] for point in bbox) / len(bbox)
            center_y = sum(point[1] for point in bbox) / len(bbox)
            
            # 바운딩 박스 크기 계산
            bbox_width = max(point[0] for point in bbox) - min(point[0] for point in bbox)
            bbox_height = max(point[1] for point in bbox) - min(point[1] for point in bbox)
            
            # 폰트 크기 결정 (바운딩 박스 크기에 비례)
            font_size = max(12, min(bbox_height * 0.8, 48))
            
            try:
                # 한글 지원 폰트 시도 (Windows)
                font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", int(font_size))  # 맑은 고딕
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/gulim.ttc", int(font_size))  # 굴림
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/batang.ttc", int(font_size))  # 바탕
                    except:
                        try:
                            font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(font_size))  # Arial
                        except:
                            # 기본 폰트 사용
                            font = ImageFont.load_default()
            
            # 텍스트 크기 측정
            bbox_text = draw.textbbox((0, 0), text, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
            
            # 텍스트 위치 계산 (중심점 기준)
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            
            # 하얀색 배경 사각형 그리기 (약간의 패딩 추가)
            padding = 4
            bg_x1 = text_x - padding
            bg_y1 = text_y - padding
            bg_x2 = text_x + text_width + padding
            bg_y2 = text_y + text_height + padding
            
            # 반투명한 하얀색 배경
            draw.rectangle([bg_x1, bg_y1, bg_x2, bg_y2], fill=(255, 255, 255, 200))
            
            # 검은색 텍스트 그리기
            draw.text((text_x, text_y), text, fill=(0, 0, 0, 255), font=font)
    
    def display_text_results(self):
        """텍스트 결과를 텍스트 영역에 표시"""
        text_content = "=== OCR 인식 결과 ===\n\n"
        
        for i, (bbox, text, confidence) in enumerate(self.ocr_results):
            text_content += f"[{i+1}] {text}\n"
            text_content += f"    신뢰도: {confidence:.2f}\n"
            text_content += f"    위치: {bbox}\n\n"
        
        # 추출된 텍스트만 따로 표시
        text_content += "=== 추출된 텍스트 ===\n"
        extracted_texts = [text for _, text, _ in self.ocr_results]
        for text in extracted_texts:
            text_content += f"{text}\n"
        
        self.text_display.setPlainText(text_content)
    
    def save_text(self):
        """텍스트 결과를 파일로 저장"""
        try:
            # 텍스트 파일로 저장
            with open("ocr_result.txt", "w", encoding="utf-8") as f:
                f.write(self.text_display.toPlainText())
            print("텍스트가 'ocr_result.txt' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"텍스트 저장 오류: {e}")
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        # 임시 파일 정리
        if os.path.exists("temp_ocr_result.jpg"):
            os.remove("temp_ocr_result.jpg")
        event.accept()
