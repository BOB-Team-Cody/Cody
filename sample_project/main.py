"""
복잡하고 리팩토링이 필요한 메인 프로그램
- 중복된 코드
- 죽은 코드 (사용되지 않는 함수들)
- 복잡한 중첩 구조
- 여러 번 호출되는 함수들
"""

import os
import sys
import json
import time
from datetime import datetime
from utils import process_data, validate_input, unused_helper, duplicate_logic
from test_runner import run_tests


class DataProcessor:
    def __init__(self):
        self.data = []
        self.config = {}
        self.results = {}
        self.cache = {}
        self.debug_mode = True
        self.log_file = "app.log"
        
    def load_config(self, config_path="config.json"):
        """설정 파일 로드 - 여러 번 호출됨"""
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    return True
            else:
                # 기본 설정 생성
                self.config = {
                    "batch_size": 100,
                    "timeout": 30,
                    "debug": True,
                    "output_format": "json"
                }
                return False
        except Exception as e:
            print(f"설정 로드 실패: {e}")
            return False

    def save_config(self, config_path="config.json"):
        """설정 파일 저장 - 사용되지 않는 함수 (DEAD CODE)"""
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                return True
        except Exception as e:
            print(f"설정 저장 실패: {e}")
            return False

    def log_message(self, message, level="INFO"):
        """로그 메시지 기록 - 여러 번 호출됨"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        if self.debug_mode:
            print(log_entry)
            
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"로그 기록 실패: {e}")

    def validate_data(self, data):
        """데이터 검증 - 복잡한 중첩 구조"""
        if not data:
            self.log_message("빈 데이터", "WARNING")
            return False
            
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    if not self.validate_dict_item(item, i):
                        return False
                elif isinstance(item, str):
                    if not self.validate_string_item(item, i):
                        return False
                elif isinstance(item, (int, float)):
                    if not self.validate_numeric_item(item, i):
                        return False
                else:
                    self.log_message(f"지원되지 않는 데이터 타입: {type(item)}", "ERROR")
                    return False
        elif isinstance(data, dict):
            return self.validate_dict_item(data, 0)
        else:
            self.log_message(f"지원되지 않는 데이터 구조: {type(data)}", "ERROR")
            return False
            
        return True

    def validate_dict_item(self, item, index):
        """딕셔너리 아이템 검증 - 여러 번 호출됨"""
        required_keys = ['id', 'name', 'value']
        for key in required_keys:
            if key not in item:
                self.log_message(f"필수 키 누락 (인덱스 {index}): {key}", "ERROR")
                return False
                
        if not isinstance(item['id'], (int, str)):
            self.log_message(f"잘못된 ID 타입 (인덱스 {index})", "ERROR")
            return False
            
        if not isinstance(item['name'], str) or len(item['name']) < 1:
            self.log_message(f"잘못된 이름 (인덱스 {index})", "ERROR")
            return False
            
        if not isinstance(item['value'], (int, float)):
            self.log_message(f"잘못된 값 타입 (인덱스 {index})", "ERROR")
            return False
            
        return True

    def validate_string_item(self, item, index):
        """문자열 아이템 검증 - 사용되지 않는 함수 (DEAD CODE)"""
        if len(item) < 1:
            self.log_message(f"빈 문자열 (인덱스 {index})", "ERROR")
            return False
        if len(item) > 1000:
            self.log_message(f"문자열이 너무 김 (인덱스 {index})", "ERROR")
            return False
        return True

    def validate_numeric_item(self, item, index):
        """숫자 아이템 검증 - 사용되지 않는 함수 (DEAD CODE)"""
        if item < 0:
            self.log_message(f"음수 값 (인덱스 {index})", "WARNING")
        if item > 1000000:
            self.log_message(f"값이 너무 큼 (인덱스 {index})", "WARNING")
        return True

    def process_batch(self, batch_data):
        """배치 데이터 처리 - 여러 번 호출됨"""
        self.log_message(f"배치 처리 시작: {len(batch_data)}개 아이템")
        
        processed_items = []
        for item in batch_data:
            try:
                # 복잡한 처리 로직 시뮬레이션
                if isinstance(item, dict):
                    processed_item = self.process_dict_item(item)
                    if processed_item:
                        processed_items.append(processed_item)
                elif isinstance(item, str):
                    processed_item = self.process_string_item(item)  # 사용되지 않는 함수 호출
                    if processed_item:
                        processed_items.append(processed_item)
                else:
                    self.log_message(f"처리할 수 없는 아이템: {item}", "WARNING")
                    
            except Exception as e:
                self.log_message(f"아이템 처리 실패: {e}", "ERROR")
                continue
                
        self.log_message(f"배치 처리 완료: {len(processed_items)}개 성공")
        return processed_items

    def process_dict_item(self, item):
        """딕셔너리 아이템 처리 - 여러 번 호출됨"""
        try:
            # 캐시 확인
            item_id = item.get('id', '')
            cache_key = f"dict_{item_id}"
            
            if cache_key in self.cache:
                self.log_message(f"캐시에서 반환: {item_id}")
                return self.cache[cache_key]
            
            # 실제 처리
            processed = {
                'id': item['id'],
                'name': item['name'].upper(),
                'value': item['value'] * 2,
                'processed_at': datetime.now().isoformat(),
                'status': 'processed'
            }
            
            # 캐시에 저장
            self.cache[cache_key] = processed
            
            return processed
            
        except KeyError as e:
            self.log_message(f"필수 키 누락: {e}", "ERROR")
            return None
        except Exception as e:
            self.log_message(f"딕셔너리 처리 실패: {e}", "ERROR")
            return None

    def process_string_item(self, item):
        """문자열 아이템 처리 - 사용되지 않는 함수 (DEAD CODE)"""
        try:
            processed = {
                'original': item,
                'length': len(item),
                'upper': item.upper(),
                'reversed': item[::-1],
                'processed_at': datetime.now().isoformat()
            }
            return processed
        except Exception as e:
            self.log_message(f"문자열 처리 실패: {e}", "ERROR")
            return None

    def generate_report(self):
        """보고서 생성 - 사용되지 않는 함수 (DEAD CODE)"""
        report = {
            'total_processed': len(self.results),
            'cache_size': len(self.cache),
            'timestamp': datetime.now().isoformat(),
            'config': self.config
        }
        
        try:
            with open('report.json', 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.log_message("보고서 생성 완료")
            return True
        except Exception as e:
            self.log_message(f"보고서 생성 실패: {e}", "ERROR")
            return False

    def cleanup_old_files(self):
        """오래된 파일 정리 - 사용되지 않는 함수 (DEAD CODE)"""
        try:
            old_files = ['old_report.json', 'temp_data.json', 'backup.json']
            for file in old_files:
                if os.path.exists(file):
                    os.remove(file)
                    self.log_message(f"파일 삭제: {file}")
            return True
        except Exception as e:
            self.log_message(f"파일 정리 실패: {e}", "ERROR")
            return False

    def run(self, input_data):
        """메인 실행 함수"""
        self.log_message("처리 시작")
        
        # 설정 로드 (여러 번 호출)
        if not self.load_config():
            self.log_message("기본 설정 사용")
        
        # 데이터 검증
        if not self.validate_data(input_data):
            self.log_message("데이터 검증 실패", "ERROR")
            return None
        
        # 배치 크기 설정
        batch_size = self.config.get('batch_size', 100)
        
        # 배치 단위로 처리
        all_results = []
        for i in range(0, len(input_data), batch_size):
            batch = input_data[i:i+batch_size]
            batch_results = self.process_batch(batch)
            all_results.extend(batch_results)
            
            # 진행률 로그
            progress = min(i + batch_size, len(input_data))
            self.log_message(f"진행률: {progress}/{len(input_data)}")
        
        self.results = all_results
        self.log_message(f"처리 완료: 총 {len(all_results)}개 결과")
        
        return all_results


def create_sample_data():
    """샘플 데이터 생성 - 여러 번 호출됨"""
    sample_data = []
    for i in range(50):
        item = {
            'id': f'item_{i:03d}',
            'name': f'데이터항목_{i}',
            'value': i * 10 + (i % 7) * 3
        }
        sample_data.append(item)
    return sample_data


def legacy_function():
    """레거시 함수 - 사용되지 않음 (DEAD CODE)"""
    old_data = []
    for i in range(10):
        old_data.append(f"legacy_item_{i}")
    return old_data


def deprecated_helper():
    """더 이상 사용되지 않는 헬퍼 함수 (DEAD CODE)"""
    return "This function is deprecated"


def main():
    """메인 함수"""
    print("=== 데이터 처리 시스템 시작 ===")
    
    # 프로세서 초기화
    processor = DataProcessor()
    
    # 샘플 데이터 생성
    sample_data = create_sample_data()
    print(f"샘플 데이터 생성: {len(sample_data)}개")
    
    # 외부 유틸리티 함수 호출 (여러 번)
    processed_sample = process_data(sample_data)  # utils.py에서 import
    
    # 입력 검증 (여러 번)
    if validate_input(processed_sample):
        print("입력 데이터 검증 통과")
    else:
        print("입력 데이터 검증 실패")
        return
    
    # 메인 처리 실행
    results = processor.run(processed_sample)
    
    if results:
        print(f"처리 결과: {len(results)}개")
        
        # 결과 출력 (처음 5개만)
        print("\n처음 5개 결과:")
        for i, result in enumerate(results[:5]):
            print(f"  {i+1}: {result}")
    else:
        print("처리 실패")
    
    # 테스트 실행
    print("\n=== 테스트 실행 ===")
    run_tests()  # test_runner.py에서 import
    
    print("\n=== 프로그램 종료 ===")


if __name__ == "__main__":
    main()