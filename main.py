import sys
import atexit
from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from capture_frame import MainFrame
from control_widget import ControlWidget
from ocr_worker import OCRWorker
from image_viewer import ImageViewer
from translate_worker import TranslateWorker


class ScreenTranslatorApp(QApplication):
    """메인 애플리케이션 클래스"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # 윈도우들 생성
        self.main_frame = MainFrame()
        self.control_widget = ControlWidget()
        
        # control_widget에서 main_frame에 접근할 수 있도록 참조 설정
        self.control_widget.main_frame = self.main_frame
        
        # OCR Worker 초기화 (기본 언어로 초기화, 나중에 동적으로 변경)
        self.ocr_worker = None
        
        # 시그널 연결
        self.control_widget.capture_requested.connect(self.handle_capture_request)
        self.control_widget.toggle_interactive.connect(self.main_frame.set_interactive_state)
        self.main_frame.deactivate_requested.connect(self.handle_deactivate_request)
        # 윈도우들 표시
        self.main_frame.show()
        self.control_widget.show()
        
        # 앱 종료 시 임시 파일 정리 등록
        atexit.register(self.cleanup_on_exit)
        
    def handle_capture_request(self, language_list):
        """캡처 요청 처리"""
        print(f"선택된 언어: {language_list}")
        
        # 캡처 전에 컨트롤 위젯 숨기기
        self.control_widget.hide()
        
        # 잠시 대기 (화면 업데이트를 위해)
        self.processEvents()
        
        # 캡처 실행
        result = self.main_frame.capture_screen()
        print(f"캡처 결과: {result}")
        
        # 캡처 후에 컨트롤 위젯 다시 보이기
        self.control_widget.show()
        
        # 캡처된 이미지와 언어 리스트를 OCR 처리에 전달
        if result and isinstance(result, dict) and result.get('success'):
            print(f"OCR 처리 시작: 이미지={result['temp_file_path']}, 언어={language_list}")
            self.process_ocr(result['temp_file_path'], language_list)
    
    def process_ocr(self, image_path, language_list):
        """OCR 처리"""
        try:
            # 언어 리스트가 변경되었거나 OCR Worker가 없으면 새로 생성
            if self.ocr_worker is None or self.ocr_worker.language_list != language_list:
                print(f"OCR Worker 초기화 중... 언어: {language_list}")
                self.ocr_worker = OCRWorker(language_list)
            
            # OCR 처리 실행
            print("OCR 처리 중...")
            result = self.ocr_worker.process_image(image_path)
            
            # 결과 출력
            print("=== OCR 결과 ===")
            for i, (bbox, text, confidence) in enumerate(result):
                print(f"{i+1}. 텍스트: '{text}' (신뢰도: {confidence:.2f})")
                print(f"   위치: {bbox}")
                print()
            
            # 추출된 텍스트만 따로 출력
            extracted_texts = [text for _, text, _ in result]
            if extracted_texts:
                print("=== 추출된 텍스트 ===")
                for text in extracted_texts:
                    print(text)
                
                # 이미지 뷰어 열기
                self.open_image_viewer(image_path, result)
            else:
                print("텍스트를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
    
    def open_image_viewer(self, image_path, ocr_results):
        """이미지 뷰어 창 열기"""
        try:
            self.image_viewer = ImageViewer(image_path, ocr_results)
            self.image_viewer.show()
        except Exception as e:
            print(f"이미지 뷰어 열기 오류: {e}")
    
    def handle_deactivate_request(self):
        """비활성화 요청 처리"""
        # 컨트롤 위젯의 상호작용 상태를 비활성화로 설정
        self.control_widget.interactive_enabled = False
        self.control_widget.toggle_button.setText("상호작용 활성화")
        self.control_widget.status_label.setText("상태: 비활성화")
        self.control_widget.show()  # 컨트롤 위젯 다시 보이기
        
        # 메인 프레임의 상호작용 상태 비활성화
        self.main_frame.set_interactive_state(False)
    
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