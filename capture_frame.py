
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QApplication, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QScreen
import tempfile
import os
from PIL import Image


class MainFrame(QMainWindow):
    """1번 화면: 빨간색 프레임, 투명 배경, 클릭 방지, 전체 화면"""
    
    # 시그널 정의
    deactivate_requested = pyqtSignal()
    
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
        
        # 비활성화 버튼 (상단 중앙에 배치)
        self.deactivate_button = QPushButton("상호작용 비활성화")
        self.deactivate_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1170a;
            }
        """)
        self.deactivate_button.clicked.connect(self.on_deactivate_clicked)
        self.deactivate_button.hide()  # 초기에는 숨김
        
        # 버튼을 상단 중앙에 배치하기 위한 레이아웃
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)  # 상단 패딩 추가
        button_layout.addWidget(self.deactivate_button, 0, Qt.AlignmentFlag.AlignHCenter)  # 중앙 정렬
        button_layout.addStretch()  # 나머지 공간을 아래로 밀어냄
        layout.addLayout(button_layout)
        
        # 내부 상태
        self.is_interactive = False
        self.capture_count = 0
        self.temp_files = []  # 생성된 임시 파일들 추적
        
        # 크기 조절 관련 상태
        self.resizing = False
        self.resize_handle = None
        self.start_pos = None
        self.start_geometry = None
        self.resize_sensitivity = 0.3  # 크기 조절 감도 (0.1 ~ 1.0) - 더 부드럽게
        
    def paintEvent(self, event):
        """빨간색 프레임과 크기 조절 핸들 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 빨간색 프레임 그리기
        pen = QPen(QColor(255, 0, 0), 3)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
        # 상호작용 활성화 시 크기 조절 핸들 그리기
        if self.is_interactive:
            handle_size = 8
            handle_color = QColor(255, 0, 0)
            
            # 모서리 핸들들
            rect = self.rect()
            # 좌상단
            painter.fillRect(0, 0, handle_size, handle_size, handle_color)
            # 우상단
            painter.fillRect(rect.width() - handle_size, 0, handle_size, handle_size, handle_color)
            # 좌하단
            painter.fillRect(0, rect.height() - handle_size, handle_size, handle_size, handle_color)
            # 우하단
            painter.fillRect(rect.width() - handle_size, rect.height() - handle_size, handle_size, handle_size, handle_color)
        
    def set_interactive_state(self, interactive):
        """상호작용 상태 설정"""
        self.is_interactive = interactive
        if interactive:
            # 상호작용 활성화: 크기 변경 가능, 최상위 유지, 반투명 배경, 비활성화 버튼 표시
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            # 반투명 흰색 배경 설정
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)  # 투명 배경 해제
            self.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")  # 반투명 흰색 배경
            # 크기 제한 해제 (최소 크기만 설정)
            self.setMinimumSize(200, 150)  # 최소 크기 설정
            self.setMaximumSize(16777215, 16777215)  # 최대 크기 제한 해제
            # 크기 조절 가능하게 설정
            self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())
            self.deactivate_button.show()  # 비활성화 버튼 표시
        else:
            # 상호작용 비활성화: 전체 화면으로 복원, 투명 배경 복원, 비활성화 버튼 숨김
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            # 투명 배경 복원
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)  # 투명 배경 복원
            self.setStyleSheet("")  # 스타일시트 초기화
            self.showFullScreen()
            self.deactivate_button.hide()  # 비활성화 버튼 숨김
        self.show()
    
    def on_deactivate_clicked(self):
        """비활성화 버튼 클릭 처리"""
        self.deactivate_requested.emit()
    
    def get_resize_handle(self, pos):
        """마우스 위치에서 크기 조절 핸들 감지"""
        if not self.is_interactive:
            return None
        
        handle_size = 8
        rect = self.rect()
        
        # 모서리 핸들들 확인
        if (pos.x() <= handle_size and pos.y() <= handle_size):
            return "top-left"
        elif (pos.x() >= rect.width() - handle_size and pos.y() <= handle_size):
            return "top-right"
        elif (pos.x() <= handle_size and pos.y() >= rect.height() - handle_size):
            return "bottom-left"
        elif (pos.x() >= rect.width() - handle_size and pos.y() >= rect.height() - handle_size):
            return "bottom-right"
        
        return None
        
    def capture_screen(self):
        """빨간색 태두리 영역을 캡처하여 임시 JPG 파일로 저장"""
        
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
        """마우스 클릭 이벤트 처리"""
        if not self.is_interactive:
            event.ignore()
            return
        
        # 크기 조절 핸들 확인
        handle = self.get_resize_handle(event.pos())
        if handle:
            self.resizing = True
            self.resize_handle = handle
            self.start_pos = event.globalPosition().toPoint()
            self.start_geometry = self.geometry()
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        else:
            # 크기 조절 핸들이 아닌 경우 윈도우 이동 허용
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if not self.is_interactive:
            return
        
        if self.resizing and self.resize_handle:
            # 크기 조절 처리 - 마우스 위치에 직접 반응
            current_pos = event.globalPosition().toPoint()
            min_size = 200, 150
            
            # 시작 지점을 기준으로 새로운 geometry 계산
            start_x = self.start_geometry.x()
            start_y = self.start_geometry.y()
            start_right = self.start_geometry.right()
            start_bottom = self.start_geometry.bottom()
            
            if self.resize_handle == "bottom-right":
                # 우하단: 마우스 위치가 새로운 우하단 모서리가 됨
                new_width = max(min_size[0], current_pos.x() - start_x)
                new_height = max(min_size[1], current_pos.y() - start_y)
                self.setGeometry(start_x, start_y, new_width, new_height)
                
            elif self.resize_handle == "bottom-left":
                # 좌하단: 마우스 위치가 새로운 좌하단 모서리가 됨
                new_width = max(min_size[0], start_right - current_pos.x())
                new_height = max(min_size[1], current_pos.y() - start_y)
                new_x = start_right - new_width
                self.setGeometry(new_x, start_y, new_width, new_height)
                
            elif self.resize_handle == "top-right":
                # 우상단: 마우스 위치가 새로운 우상단 모서리가 됨
                new_width = max(min_size[0], current_pos.x() - start_x)
                new_height = max(min_size[1], start_bottom - current_pos.y())
                new_y = start_bottom - new_height
                self.setGeometry(start_x, new_y, new_width, new_height)
                
            elif self.resize_handle == "top-left":
                # 좌상단: 마우스 위치가 새로운 좌상단 모서리가 됨
                new_width = max(min_size[0], start_right - current_pos.x())
                new_height = max(min_size[1], start_bottom - current_pos.y())
                new_x = start_right - new_width
                new_y = start_bottom - new_height
                self.setGeometry(new_x, new_y, new_width, new_height)
        elif hasattr(self, 'drag_position') and event.buttons() == Qt.MouseButton.LeftButton:
            # 윈도우 이동 처리
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
        else:
            # 커서 변경
            handle = self.get_resize_handle(event.pos())
            if handle:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """마우스 릴리즈 이벤트 처리"""
        if self.resizing:
            self.resizing = False
            self.resize_handle = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
