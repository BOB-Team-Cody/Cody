"""
유틸리티 함수 모듈
- 자주 사용되는 함수들
- 죽은 코드 함수들
- 중복된 로직을 포함한 함수들
"""

import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


def process_data(data: List[Dict]) -> List[Dict]:
    """데이터 전처리 함수 - 자주 호출됨"""
    if not data:
        return []
    
    processed = []
    for item in data:
        if isinstance(item, dict):
            # 데이터 정규화
            normalized_item = normalize_data_item(item)
            if normalized_item:
                processed.append(normalized_item)
        else:
            print(f"잘못된 데이터 형식: {type(item)}")
    
    return processed


def normalize_data_item(item: Dict) -> Optional[Dict]:
    """데이터 아이템 정규화 - 여러 번 호출됨"""
    try:
        normalized = {}
        
        # ID 정규화
        if 'id' in item:
            normalized['id'] = str(item['id']).strip()
        else:
            normalized['id'] = generate_id()
        
        # 이름 정규화
        if 'name' in item:
            normalized['name'] = clean_string(item['name'])
        else:
            normalized['name'] = "Unknown"
        
        # 값 정규화
        if 'value' in item:
            normalized['value'] = normalize_numeric_value(item['value'])
        else:
            normalized['value'] = 0
        
        # 추가 메타데이터
        normalized['normalized_at'] = datetime.now().isoformat()
        normalized['checksum'] = calculate_checksum(normalized)
        
        return normalized
        
    except Exception as e:
        print(f"정규화 실패: {e}")
        return None


def validate_input(data: Any) -> bool:
    """입력 데이터 검증 - 여러 번 호출됨"""
    if not data:
        print("빈 데이터입니다.")
        return False
    
    if not isinstance(data, list):
        print("리스트 형태의 데이터가 아닙니다.")
        return False
    
    if len(data) == 0:
        print("데이터가 비어있습니다.")
        return False
    
    # 각 아이템 검증
    valid_items = 0
    for i, item in enumerate(data):
        if validate_data_item(item):
            valid_items += 1
        else:
            print(f"유효하지 않은 아이템 (인덱스 {i}): {item}")
    
    # 최소 80% 이상이 유효해야 함
    validation_ratio = valid_items / len(data)
    if validation_ratio < 0.8:
        print(f"유효한 데이터 비율이 낮습니다: {validation_ratio:.2%}")
        return False
    
    print(f"데이터 검증 통과: {valid_items}/{len(data)} 유효")
    return True


def validate_data_item(item: Any) -> bool:
    """개별 데이터 아이템 검증 - 여러 번 호출됨"""
    if not isinstance(item, dict):
        return False
    
    # 필수 필드 확인
    required_fields = ['id', 'name', 'value']
    for field in required_fields:
        if field not in item:
            return False
    
    # 데이터 타입 확인
    if not isinstance(item['name'], str):
        return False
    
    if not isinstance(item['value'], (int, float)):
        return False
    
    return True


def clean_string(text: str) -> str:
    """문자열 정리 함수 - 여러 번 호출됨"""
    if not isinstance(text, str):
        return ""
    
    # 앞뒤 공백 제거
    cleaned = text.strip()
    
    # 연속된 공백을 하나로
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # 특수 문자 제거 (알파벳, 숫자, 한글, 일부 특수문자만 유지)
    cleaned = re.sub(r'[^\w\s가-힣\-_]', '', cleaned)
    
    return cleaned


def normalize_numeric_value(value: Any) -> float:
    """숫자 값 정규화 - 여러 번 호출됨"""
    try:
        if isinstance(value, str):
            # 문자열에서 숫자만 추출
            numeric_str = re.sub(r'[^\d.-]', '', value)
            return float(numeric_str) if numeric_str else 0.0
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return 0.0
    except (ValueError, TypeError):
        return 0.0


def generate_id() -> str:
    """고유 ID 생성 - 여러 번 호출됨"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    return f"auto_{timestamp}"


def calculate_checksum(data: Dict) -> str:
    """데이터 체크섬 계산 - 여러 번 호출됨"""
    try:
        # 정렬된 JSON 문자열 생성
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        # MD5 해시 계산
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()
    except Exception:
        return "checksum_error"


def duplicate_logic(data: List[Dict]) -> List[Dict]:
    """중복된 로직을 포함한 함수 - 사용되지 않음 (DEAD CODE)"""
    # process_data 함수와 거의 동일한 로직
    if not data:
        return []
    
    processed = []
    for item in data:
        if isinstance(item, dict):
            # 거의 동일한 정규화 로직
            normalized_item = {}
            
            if 'id' in item:
                normalized_item['id'] = str(item['id']).strip()
            else:
                normalized_item['id'] = f"dup_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            if 'name' in item:
                name = item['name'].strip()
                name = re.sub(r'\s+', ' ', name)
                normalized_item['name'] = name
            else:
                normalized_item['name'] = "Duplicate_Unknown"
            
            if 'value' in item:
                try:
                    normalized_item['value'] = float(item['value'])
                except (ValueError, TypeError):
                    normalized_item['value'] = 0.0
            else:
                normalized_item['value'] = 0
            
            processed.append(normalized_item)
    
    return processed


def unused_helper(text: str) -> str:
    """사용되지 않는 헬퍼 함수 (DEAD CODE)"""
    return text.upper().replace(" ", "_")


def legacy_data_converter(old_format_data: List) -> List[Dict]:
    """레거시 데이터 변환 함수 - 사용되지 않음 (DEAD CODE)"""
    converted = []
    for i, item in enumerate(old_format_data):
        if isinstance(item, str):
            converted_item = {
                'legacy_id': f"legacy_{i}",
                'legacy_name': item,
                'legacy_value': len(item),
                'converted_at': datetime.now().isoformat()
            }
            converted.append(converted_item)
    return converted


def old_validation_function(data: Any) -> bool:
    """오래된 검증 함수 - 사용되지 않음 (DEAD CODE)"""
    # 구버전 검증 로직
    if data is None:
        return False
    
    if len(str(data)) < 1:
        return False
    
    return True


def deprecated_string_processor(text: str) -> str:
    """더 이상 사용되지 않는 문자열 처리기 (DEAD CODE)"""
    processed = text.lower()
    processed = processed.replace("old", "new")
    processed = processed.replace("legacy", "modern")
    return processed


def complex_nested_function(data: List[Dict]) -> Dict:
    """복잡한 중첩 함수 - 사용되지 않음 (DEAD CODE)"""
    result = {'processed': 0, 'errors': 0, 'warnings': 0}
    
    for item in data:
        try:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        if len(value) > 100:
                            result['warnings'] += 1
                        elif len(value) == 0:
                            result['errors'] += 1
                        else:
                            result['processed'] += 1
                    elif isinstance(value, (int, float)):
                        if value < 0:
                            result['warnings'] += 1
                        elif value == 0:
                            result['errors'] += 1
                        else:
                            result['processed'] += 1
                    else:
                        result['errors'] += 1
            else:
                result['errors'] += 1
        except Exception:
            result['errors'] += 1
    
    return result


def backup_data(data: List[Dict], filename: str = None) -> bool:
    """데이터 백업 함수 - 사용되지 않음 (DEAD CODE)"""
    try:
        if not filename:
            filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"백업 완료: {filename}")
        return True
    except Exception as e:
        print(f"백업 실패: {e}")
        return False


def restore_data(filename: str) -> Optional[List[Dict]]:
    """데이터 복원 함수 - 사용되지 않음 (DEAD CODE)"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"복원 완료: {filename}")
        return data
    except Exception as e:
        print(f"복원 실패: {e}")
        return None


def performance_monitor():
    """성능 모니터링 함수 - 사용되지 않음 (DEAD CODE)"""
    import psutil
    import time
    
    start_time = time.time()
    cpu_percent = psutil.cpu_percent()
    memory_info = psutil.virtual_memory()
    
    return {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': cpu_percent,
        'memory_percent': memory_info.percent,
        'execution_time': time.time() - start_time
    }


def format_output(data: Any, format_type: str = 'json') -> str:
    """출력 포맷팅 함수 - 사용되지 않음 (DEAD CODE)"""
    try:
        if format_type.lower() == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format_type.lower() == 'csv':
            # CSV 포맷팅 로직 (미완성)
            return str(data)
        else:
            return str(data)
    except Exception as e:
        return f"포맷팅 오류: {e}"