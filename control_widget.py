



from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt, pyqtSignal


class ControlWidget(QMainWindow):
    """2번 화면: 컨트롤 위젯 (캡처 버튼)"""
    
    # 시그널 정의
    capture_requested = pyqtSignal()
    toggle_interactive = pyqtSignal(bool)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Widget")
        # 상단 바 제거하되 자유롭게 움직일 수 있도록 설정
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # 윈도우 크기 설정
        self.setGeometry(600, 100, 200, 150)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 스타일 설정
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                border: 2px solid #333;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                font-size: 12px;
                color: #333;
                text-align: center;
            }
        """)
        
        # 캡처 버튼
        self.capture_button = QPushButton("캡처")
        self.capture_button.clicked.connect(self.on_capture_clicked)
        layout.addWidget(self.capture_button)
        
        # 상태 토글 버튼
        self.toggle_button = QPushButton("상호작용 활성화")
        self.toggle_button.clicked.connect(self.on_toggle_clicked)
        layout.addWidget(self.toggle_button)
        
        # 상태 표시 레이블
        self.status_label = QLabel("상태: 비활성화")
        layout.addWidget(self.status_label)
        
        # 종료 버튼
        self.exit_button = QPushButton("종료")
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c1170a;
            }
        """)
        self.exit_button.clicked.connect(self.close_application)
        layout.addWidget(self.exit_button)
        
        # 내부 상태
        self.interactive_enabled = False
        
    def on_capture_clicked(self):
        """캡처 버튼 클릭 처리"""
        self.capture_requested.emit()
        
    def on_toggle_clicked(self):
        """상호작용 토글 버튼 클릭 처리"""
        self.interactive_enabled = not self.interactive_enabled
        self.toggle_interactive.emit(self.interactive_enabled)
        
        if self.interactive_enabled:
            # 상호작용 활성화 시: 컨트롤 위젯 숨기기
            self.hide()
        else:
            # 상호작용 비활성화 시: 컨트롤 위젯 보이기
            self.show()
            self.toggle_button.setText("상호작용 활성화")
            self.status_label.setText("상태: 비활성화")
    
    def close_application(self):
        """애플리케이션 종료"""
        # 임시 파일 정리 후 종료 (메서드가 있는 경우에만)
        if hasattr(self, 'main_frame') and hasattr(self.main_frame, 'cleanup_temp_files'):
            self.main_frame.cleanup_temp_files()
        QApplication.quit()
    
    def mousePressEvent(self, event):
        """마우스 클릭으로 윈도우 이동 가능하게 설정"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """마우스 드래그로 윈도우 이동"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()