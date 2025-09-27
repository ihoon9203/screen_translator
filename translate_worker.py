import requests
import json
import os


class TranslateWorker:
    """Google Cloud 번역 API를 사용하는 번역 워커"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
    
    def translate_text(self, text, target_language='ko', source_language='auto'):
        """
        텍스트를 번역합니다.
        
        Args:
            text (str): 번역할 텍스트
            target_language (str): 목표 언어 (기본값: 'ko' - 한국어)
            source_language (str): 원본 언어 (기본값: 'auto' - 자동 감지)
        
        Returns:
            dict: 번역 결과
        """
        try:
            # API 요청 파라미터
            params = {
                'key': self.api_key,
                'q': text,
                'target': target_language,
                'source': source_language,
                'format': 'text'
            }
            
            # API 요청
            response = requests.post(self.base_url, data=params)
            response.raise_for_status()
            
            # 응답 파싱
            result = response.json()
            
            if 'data' in result and 'translations' in result['data']:
                translation = result['data']['translations'][0]
                return {
                    'success': True,
                    'translated_text': translation['translatedText'],
                    'detected_language': translation.get('detectedSourceLanguage', source_language),
                    'original_text': text
                }
            else:
                return {
                    'success': False,
                    'error': '번역 결과를 찾을 수 없습니다.',
                    'original_text': text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API 요청 오류: {str(e)}',
                'original_text': text
            }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'JSON 파싱 오류: {str(e)}',
                'original_text': text
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'예상치 못한 오류: {str(e)}',
                'original_text': text
            }
    
    def translate_multiple(self, texts, target_language='ko', source_language='auto'):
        """
        여러 텍스트를 한 번에 번역합니다.
        
        Args:
            texts (list): 번역할 텍스트 리스트
            target_language (str): 목표 언어
            source_language (str): 원본 언어
        
        Returns:
            list: 번역 결과 리스트
        """
        results = []
        for text in texts:
            result = self.translate_text(text, target_language, source_language)
            results.append(result)
        return results
    
    def get_supported_languages(self):
        """
        지원되는 언어 목록을 가져옵니다.
        
        Returns:
            dict: 언어 목록
        """
        try:
            url = f"https://translation.googleapis.com/language/translate/v2/languages"
            params = {'key': self.api_key}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'languages': result.get('data', {}).get('languages', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'언어 목록 조회 오류: {str(e)}'
            }


# 테스트용 코드
if __name__ == "__main__":
    # API 키를 여기에 입력하세요
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("API 키를 설정해주세요!")
    else:
        worker = TranslateWorker(API_KEY)
        
        # 테스트 번역
        result = worker.translate_text("Hello, world!", target_language='ko')
        print("번역 결과:", result)
        
        # 지원 언어 확인
        languages = worker.get_supported_languages()
        print("지원 언어:", languages)

