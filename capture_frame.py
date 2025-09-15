
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QScreen
import tempfile
import os
from PIL import Image


class MainFrame(QMainWindow):
    """1번 화면: 빨간색 프레임, 투명 배경, 클릭 방지, 전체 화면"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Frame")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 전체 화면 설정
        self.showFullScreen()
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        
        # 내부 상태
        self.is_interactive = False
        self.capture_count = 0
        self.temp_files = []  # 생성된 임시 파일들 추적
        
    def paintEvent(self, event):
        """빨간색 프레임 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 빨간색 프레임 그리기
        pen = QPen(QColor(255, 0, 0), 3)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
    def set_interactive_state(self, interactive):
        """상호작용 상태 설정"""
        self.is_interactive = interactive
        if interactive:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.show()
        
    def capture_screen(self):
        """빨간색 태두리 영역을 캡처하여 임시 JPG 파일로 저장"""
        if not self.is_interactive:
            return "상태가 비활성화되어 있습니다."
        
        try:
            # 현재 화면 가져오기
            app = QApplication.instance()
            screen = app.primaryScreen()
            
            # 현재 윈도우의 위치와 크기 가져오기
            window_geometry = self.geometry()
            
            # 빨간색 태두리 영역 계산 (태두리 두께 3픽셀 고려)
            border_thickness = 3
            capture_rect = window_geometry.adjusted(
                border_thickness, 
                border_thickness, 
                -border_thickness, 
                -border_thickness
            )
            
            # 화면 캡처
            screenshot = screen.grabWindow(0, 
                                        capture_rect.x(), 
                                        capture_rect.y(), 
                                        capture_rect.width(), 
                                        capture_rect.height())
            
            # QPixmap을 임시 PNG로 저장한 후 PIL로 읽기 (색상 보존)
            temp_png = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_png_path = temp_png.name
            temp_png.close()
            
            # QPixmap을 PNG로 저장
            screenshot.save(temp_png_path, "PNG")
            
            # PIL로 PNG 읽기
            pil_image = Image.open(temp_png_path)
            
            # RGB로 변환 (색상 보존)
            rgb_image = pil_image.convert("RGB")
            
            # 임시 PNG 파일 삭제
            os.unlink(temp_png_path)
            
            # 임시 JPG 파일 생성
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            temp_file_path = temp_file.name
            temp_file.close()
            
            # JPG로 저장
            rgb_image.save(temp_file_path, 'JPEG', quality=95)
            
            # 임시 파일 목록에 추가
            self.temp_files.append(temp_file_path)
            
            self.capture_count += 1
            
            return {
                'success': True,
                'message': f"캡처 완료! ({self.capture_count}번째)",
                'temp_file_path': temp_file_path,
                'capture_rect': {
                    'x': capture_rect.x(),
                    'y': capture_rect.y(),
                    'width': capture_rect.width(),
                    'height': capture_rect.height()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f"캡처 실패: {str(e)}",
                'temp_file_path': None
            }
    
    def cleanup_temp_files(self):
        """생성된 임시 파일들 정리"""
        for temp_file_path in self.temp_files:
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except Exception as e:
                print(f"임시 파일 삭제 실패: {temp_file_path}, 오류: {e}")
        self.temp_files.clear()
    
    def get_latest_capture(self):
        """가장 최근 캡처된 파일 경로 반환"""
        if self.temp_files:
            return self.temp_files[-1]
        return None
    
    def mousePressEvent(self, event):
        """클릭 이벤트 처리 - 상호작용 상태가 아닐 때 클릭 방지"""
        if not self.is_interactive:
            event.ignore()
            return
        super().mousePressEvent(event)
