



from PySide6.QtWidgets import QComboBox, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QApplication, QCheckBox, QGroupBox, QHBoxLayout
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal, QSettings
from qt_material import apply_stylesheet


class ControlWidget(QMainWindow):
    """2번 화면: 컨트롤 위젯 (캡처 버튼)"""
    
    # 시그널 정의
    capture_requested = Signal(list)  # 언어 리스트를 함께 전달
    toggle_interactive = Signal(bool)
    color_mod_request = Signal(QColor)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Widget")
        # 상단 바 제거하되 자유롭게 움직일 수 있도록 설정
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # 윈도우 크기 설정 (언어 선택을 위해 높이 증가)
        self.setGeometry(600, 100, 200, 250)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃 설정
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # qt_material 테마 적용
        self.setStyleSheet(apply_stylesheet(QApplication.instance(), theme='dark_teal.xml'))
        
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

        empty_widget = QWidget()
        empty_widget.setFixedHeight(10)
        layout.addWidget(empty_widget)

        self.designated_language_dropdown = QComboBox()
        self.designated_language_dropdown.setPlaceholderText("output language")
        self.designated_language_dropdown.addItems(['한국어(ko)', 'English(en)', '日本語(ja)', '中文(ch_sim)', 'Español(es)'])
        self.designated_language_dropdown.currentTextChanged.connect(self.on_language_changed)
        layout.addWidget(self.designated_language_dropdown)
        
        # 언어 선택 그룹
        language_group = QGroupBox("언어 선택")
        language_layout = QVBoxLayout(language_group)
        
        # 언어 체크박스들
        self.korean_checkbox = QCheckBox("한국어 (ko)")
        self.korean_checkbox.setChecked(True)  # 기본값으로 한국어 선택
        self.korean_checkbox.stateChanged.connect(self.on_language_changed)
        
        self.english_checkbox = QCheckBox("영어 (en)")
        self.english_checkbox.setChecked(True)  # 기본값으로 영어 선택
        self.english_checkbox.stateChanged.connect(self.on_language_changed)
        
        self.japanese_checkbox = QCheckBox("일본어 (ja)")
        self.japanese_checkbox.stateChanged.connect(self.on_language_changed)
        
        self.chinese_checkbox = QCheckBox("중국어 (ch_sim)")
        self.chinese_checkbox.stateChanged.connect(self.on_language_changed)
        
        self.spanish_checkbox = QCheckBox("스페인어 (es)")
        self.spanish_checkbox.stateChanged.connect(self.on_language_changed)
        
        # 체크박스들은 qt_material 테마가 자동으로 스타일링
        
        language_layout.addWidget(self.korean_checkbox)
        language_layout.addWidget(self.english_checkbox)
        language_layout.addWidget(self.japanese_checkbox)
        language_layout.addWidget(self.chinese_checkbox)
        language_layout.addWidget(self.spanish_checkbox)

        layout.addWidget(language_group)
        
        # 종료 버튼
        self.exit_button = QPushButton("종료")
        self.exit_button.clicked.connect(self.close_application)
        layout.addWidget(self.exit_button)
        
        # 내부 상태
        self.interactive_enabled = False
        self.selected_languages = []
        self.target_language = ""

        self.colorPanel = SimpleColorPalette(self.color_mod_request, self) 
        layout.addWidget(self.colorPanel)

        # 모든 위젯 생성 후 이전 세션 값 로드
        self.load_settings()
    def _create_spacer(self, height):
        """높이 지정된 빈 공간 생성"""
        w = QWidget()
        w.setFixedHeight(height)
        return w
    def on_color_selected(self):
        print()
    def save_settings(self):
        """체크박스와 드롭다운 상태 저장"""
        # 체크박스 상태
        self.settings.setValue("lang/ko", self.korean_checkbox.isChecked())
        self.settings.setValue("lang/en", self.english_checkbox.isChecked())
        self.settings.setValue("lang/ja", self.japanese_checkbox.isChecked())
        self.settings.setValue("lang/ch_sim", self.chinese_checkbox.isChecked())
        self.settings.setValue("lang/es", self.spanish_checkbox.isChecked())
        print(f"selected: {self.designated_language_dropdown.currentText()}")
        # 드롭다운 상태 (현재 텍스트 기준)
        self.settings.setValue("target_language", self.designated_language_dropdown.currentText())
        target_lang = str(self.settings.value("target_language"))
        print(f"target: {target_lang}")

    def load_settings(self):
        """체크박스와 드롭다운 상태 복원"""
        print(f"korean: {self.settings.value("lang/ko", True, type=bool)}")
        print(f"english: {self.settings.value("lang/en", True, type=bool)}")
        print(f"japanese: {self.settings.value("lang/ja", True, type=bool)}")
        print(f"chinese: {self.settings.value("lang/ch_sim", True, type=bool)}")
        print(f"espanol: {self.settings.value("lang/es", True, type=bool)}")
        print(f"target: {self.settings.value("target_language", type=str)}")
        korean = self.settings.value("lang/ko", True, type=bool)
        english = self.settings.value("lang/en", True, type=bool)
        japanese = self.settings.value("lang/ja", True, type=bool)
        chinese = self.settings.value("lang/ch_sim", True, type=bool)
        espanol = self.settings.value("lang/es", True, type=bool)
        
    def on_capture_clicked(self):
        """캡처 버튼 클릭 처리"""
        # 현재 선택된 언어 리스트와 함께 캡처 요청
        self.capture_requested.emit(self.get_selected_languages())
        
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
    
    def on_language_changed(self):
        """언어 선택 변경 처리"""
        self.selected_languages = []
        
        if self.korean_checkbox.isChecked():
            self.selected_languages.append('ko')
        if self.english_checkbox.isChecked():
            self.selected_languages.append('en')
        if self.japanese_checkbox.isChecked():
            self.selected_languages.append('ja')
        if self.chinese_checkbox.isChecked():
            self.selected_languages.append('ch_sim')
        if self.spanish_checkbox.isChecked():
            self.selected_languages.append('es')
        
        # 최소 하나의 언어는 선택되어야 함
        if not self.selected_languages:
            # 모든 언어가 해제되면 한국어를 다시 선택
            self.korean_checkbox.setChecked(True)
            self.selected_languages = ['ko']
        
        print(f"선택된 언어: {self.selected_languages}")
    
    def get_selected_languages(self):
        """선택된 언어 목록 반환"""
        return self.selected_languages
    
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


class SimpleColorPalette(QWidget,):
    """빨강, 초록, 파랑, 투명색 선택 패널"""

    def __init__(self, color_mod_request_signal, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        colors = {
            "빨강": "#FF0000",
            "초록": "#00FF00",
            "파랑": "#0000FF",
            "투명": "transparent"
        }

        for name, hex_color in colors.items():
            btn = QPushButton()
            btn.setFixedSize(40, 40)
            btn.setToolTip(name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    border: 2px solid #888;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    border: 2px solid #000;
                }}
            """)
            # SimpleColorPalette 클래스 내부 (수정)
# lambda를 사용하여 클릭 시점에 QColor 객체를 인수로 전달하며 color_selected 시그널을 방출
            btn.clicked.connect(lambda _, c=hex_color: color_mod_request_signal.emit(QColor(c)))
            layout.addWidget(btn)
