import sys
import atexit
from PyQt6.QtWidgets import QApplication
from capture_frame import MainFrame
from control_widget import ControlWidget


class ScreenTranslatorApp(QApplication):
    """메인 애플리케이션 클래스"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # 윈도우들 생성
        self.main_frame = MainFrame()
        self.control_widget = ControlWidget()
        
        # control_widget에서 main_frame에 접근할 수 있도록 참조 설정
        self.control_widget.main_frame = self.main_frame
        
        # 시그널 연결
        self.control_widget.capture_requested.connect(self.handle_capture_request)
        self.control_widget.toggle_interactive.connect(self.main_frame.set_interactive_state)
        
        # 윈도우들 표시
        self.main_frame.show()
        self.control_widget.show()
        
        # 앱 종료 시 임시 파일 정리 등록
        atexit.register(self.cleanup_on_exit)
        
    def handle_capture_request(self):
        """캡처 요청 처리"""
        # 캡처 전에 컨트롤 위젯 숨기기
        self.control_widget.hide()
        
        # 잠시 대기 (화면 업데이트를 위해)
        self.processEvents()
        
        # 캡처 실행
        result = self.main_frame.capture_screen()
        print(f"캡처 결과: {result}")
        
        # 캡처 후에 컨트롤 위젯 다시 보이기
        self.control_widget.show()
    
    def cleanup_on_exit(self):
        """앱 종료 시 임시 파일들 정리"""
        print("앱 종료 중... 임시 파일들을 정리합니다.")
        if hasattr(self.main_frame, 'cleanup_temp_files'):
            self.main_frame.cleanup_temp_files()


def main():
    app = ScreenTranslatorApp(sys.argv)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()