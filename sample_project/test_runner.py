"""
테스트 실행기 모듈
- 여러 번 호출되는 테스트 함수들
- 사용되지 않는 테스트 함수들 (DEAD CODE)
- 중복된 테스트 로직
"""

import unittest
import sys
import time
from datetime import datetime
from typing import List, Dict, Any
from utils import process_data, validate_input, normalize_data_item, clean_string


class TestDataProcessor(unittest.TestCase):
    """데이터 처리기 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정 - 각 테스트마다 호출됨"""
        self.sample_data = [
            {'id': 'test_001', 'name': '테스트 데이터 1', 'value': 100},
            {'id': 'test_002', 'name': '테스트 데이터 2', 'value': 200},
            {'id': 'test_003', 'name': '테스트 데이터 3', 'value': 300}
        ]
        self.invalid_data = [
            {'name': '이름만 있음', 'value': 100},  # ID 누락
            {'id': 'test_004', 'value': 400},       # name 누락
            {'id': 'test_005', 'name': '값 누락'}   # value 누락
        ]
        self.empty_data = []
        
    def tearDown(self):
        """테스트 정리 - 각 테스트마다 호출됨"""
        # 테스트 후 정리 작업
        pass
        
    def test_process_data_valid_input(self):
        """유효한 데이터 처리 테스트 - 실행됨"""
        result = process_data(self.sample_data)
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        self.assertEqual(len(result), len(self.sample_data))
        
    def test_process_data_empty_input(self):
        """빈 데이터 처리 테스트 - 실행됨"""
        result = process_data(self.empty_data)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 0)
        
    def test_validate_input_valid_data(self):
        """유효한 입력 검증 테스트 - 실행됨"""
        result = validate_input(self.sample_data)
        self.assertTrue(result)
        
    def test_validate_input_invalid_data(self):
        """유효하지 않은 입력 검증 테스트 - 실행됨"""
        result = validate_input(self.invalid_data)
        self.assertFalse(result)
        
    def test_validate_input_empty_data(self):
        """빈 입력 검증 테스트 - 실행됨"""
        result = validate_input(self.empty_data)
        self.assertFalse(result)
        
    def test_normalize_data_item(self):
        """데이터 아이템 정규화 테스트 - 실행됨"""
        item = self.sample_data[0]
        result = normalize_data_item(item)
        self.assertIsNotNone(result)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertIn('value', result)
        self.assertIn('normalized_at', result)
        
    def test_clean_string(self):
        """문자열 정리 테스트 - 실행됨"""
        test_string = "  테스트   문자열   "
        result = clean_string(test_string)
        self.assertEqual(result, "테스트 문자열")
        
    # 사용되지 않는 테스트 함수들 (DEAD CODE)
    def test_legacy_function_unused(self):
        """레거시 함수 테스트 - 사용되지 않음 (DEAD CODE)"""
        # 이 테스트는 실행되지 않음
        self.assertTrue(True)
        
    def test_deprecated_feature(self):
        """더 이상 사용되지 않는 기능 테스트 (DEAD CODE)"""
        # 이 테스트는 실행되지 않음
        deprecated_result = "deprecated"
        self.assertEqual(deprecated_result, "deprecated")


class TestUtilityFunctions(unittest.TestCase):
    """유틸리티 함수 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정 - 각 테스트마다 호출됨"""
        self.test_data = {
            'id': 'util_test_001',
            'name': '유틸리티 테스트',
            'value': 500
        }
    
    def test_string_operations(self):
        """문자열 연산 테스트 - 실행됨"""
        test_strings = [
            "  공백이 있는 문자열  ",
            "특수문자!@#$%포함된^&*문자열",
            "정상적인 문자열"
        ]
        
        for test_string in test_strings:
            result = clean_string(test_string)
            self.assertIsInstance(result, str)
            # 앞뒤 공백이 제거되었는지 확인
            self.assertEqual(result, result.strip())
    
    def test_data_validation_edge_cases(self):
        """데이터 검증 경계 케이스 테스트 - 실행됨"""
        edge_cases = [
            None,
            [],
            {},
            "문자열",
            123,
            [{'invalid': 'data'}]
        ]
        
        for case in edge_cases:
            result = validate_input(case)
            # None, 빈 리스트, 잘못된 형식은 False여야 함
            if case in [None, [], "문자열", 123]:
                self.assertFalse(result)
    
    # 사용되지 않는 테스트 함수들 (DEAD CODE)
    def test_unused_validation_logic(self):
        """사용되지 않는 검증 로직 테스트 (DEAD CODE)"""
        # 이 테스트는 호출되지 않음
        unused_data = ["old", "legacy", "deprecated"]
        self.assertEqual(len(unused_data), 3)
    
    def test_old_string_processing(self):
        """오래된 문자열 처리 테스트 (DEAD CODE)"""
        # 이 테스트는 호출되지 않음
        old_string = "old legacy string"
        self.assertIn("old", old_string)


class TestPerformance(unittest.TestCase):
    """성능 테스트 클래스 - 사용되지 않음 (DEAD CODE)"""
    
    def setUp(self):
        self.large_dataset = []
        for i in range(1000):
            self.large_dataset.append({
                'id': f'perf_test_{i:04d}',
                'name': f'성능 테스트 데이터 {i}',
                'value': i * 2
            })
    
    def test_large_dataset_processing(self):
        """대용량 데이터셋 처리 성능 테스트 (DEAD CODE)"""
        start_time = time.time()
        result = process_data(self.large_dataset)
        end_time = time.time()
        
        processing_time = end_time - start_time
        self.assertLess(processing_time, 5.0)  # 5초 이내에 완료되어야 함
        self.assertEqual(len(result), len(self.large_dataset))
    
    def test_memory_usage(self):
        """메모리 사용량 테스트 (DEAD CODE)"""
        import sys
        
        initial_size = sys.getsizeof(self.large_dataset)
        processed_data = process_data(self.large_dataset)
        final_size = sys.getsizeof(processed_data)
        
        # 처리된 데이터가 원본보다 크게 증가하지 않아야 함
        self.assertLess(final_size, initial_size * 3)


class TestLegacyFeatures(unittest.TestCase):
    """레거시 기능 테스트 클래스 - 전체가 사용되지 않음 (DEAD CODE)"""
    
    def setUp(self):
        """레거시 테스트 설정"""
        self.legacy_data = ["old_item_1", "old_item_2", "old_item_3"]
        self.deprecated_config = {
            "old_setting": True,
            "legacy_mode": "enabled",
            "deprecated_feature": "active"
        }
    
    def test_legacy_data_conversion(self):
        """레거시 데이터 변환 테스트 (DEAD CODE)"""
        # 이 전체 클래스는 사용되지 않음
        converted = []
        for item in self.legacy_data:
            converted.append(f"converted_{item}")
        
        self.assertEqual(len(converted), len(self.legacy_data))
    
    def test_deprecated_configuration(self):
        """더 이상 사용되지 않는 설정 테스트 (DEAD CODE)"""
        # 이 테스트는 실행되지 않음
        self.assertTrue(self.deprecated_config["old_setting"])
        self.assertEqual(self.deprecated_config["legacy_mode"], "enabled")
    
    def test_old_api_compatibility(self):
        """구 API 호환성 테스트 (DEAD CODE)"""
        # 이 테스트는 실행되지 않음
        old_api_response = {"status": "deprecated", "data": None}
        self.assertEqual(old_api_response["status"], "deprecated")


def run_basic_tests():
    """기본 테스트 실행 - 여러 번 호출됨"""
    print("=== 기본 테스트 실행 ===")
    
    # 테스트 스위트 생성
    test_suite = unittest.TestSuite()
    
    # 데이터 처리기 테스트 추가
    test_suite.addTest(TestDataProcessor('test_process_data_valid_input'))
    test_suite.addTest(TestDataProcessor('test_process_data_empty_input'))
    test_suite.addTest(TestDataProcessor('test_validate_input_valid_data'))
    test_suite.addTest(TestDataProcessor('test_validate_input_invalid_data'))
    test_suite.addTest(TestDataProcessor('test_normalize_data_item'))
    test_suite.addTest(TestDataProcessor('test_clean_string'))
    
    # 유틸리티 함수 테스트 추가
    test_suite.addTest(TestUtilityFunctions('test_string_operations'))
    test_suite.addTest(TestUtilityFunctions('test_data_validation_edge_cases'))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 결과 요약
    print(f"\n테스트 실행 완료:")
    print(f"  - 실행된 테스트: {result.testsRun}")
    print(f"  - 실패: {len(result.failures)}")
    print(f"  - 오류: {len(result.errors)}")
    
    return result.wasSuccessful()


def run_extended_tests():
    """확장 테스트 실행 - 사용되지 않음 (DEAD CODE)"""
    print("=== 확장 테스트 실행 ===")
    
    # 모든 테스트 클래스 실행
    test_classes = [TestDataProcessor, TestUtilityFunctions, TestPerformance, TestLegacyFeatures]
    
    all_tests = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        all_tests.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)
    
    return result.wasSuccessful()


def run_performance_tests():
    """성능 테스트만 실행 - 사용되지 않음 (DEAD CODE)"""
    print("=== 성능 테스트 실행 ===")
    
    performance_suite = unittest.TestSuite()
    performance_suite.addTest(TestPerformance('test_large_dataset_processing'))
    performance_suite.addTest(TestPerformance('test_memory_usage'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(performance_suite)
    
    return result.wasSuccessful()


def run_legacy_tests():
    """레거시 테스트 실행 - 사용되지 않음 (DEAD CODE)"""
    print("=== 레거시 테스트 실행 ===")
    
    legacy_suite = unittest.TestSuite()
    legacy_suite.addTest(TestLegacyFeatures('test_legacy_data_conversion'))
    legacy_suite.addTest(TestLegacyFeatures('test_deprecated_configuration'))
    legacy_suite.addTest(TestLegacyFeatures('test_old_api_compatibility'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(legacy_suite)
    
    return result.wasSuccessful()


def benchmark_functions():
    """함수 벤치마크 - 사용되지 않음 (DEAD CODE)"""
    print("=== 함수 벤치마크 ===")
    
    # 샘플 데이터 생성
    sample_data = []
    for i in range(100):
        sample_data.append({
            'id': f'bench_{i:03d}',
            'name': f'벤치마크 데이터 {i}',
            'value': i * 5
        })
    
    # process_data 함수 벤치마크
    start_time = time.time()
    for _ in range(10):
        process_data(sample_data)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 10
    print(f"process_data 평균 실행 시간: {avg_time:.4f}초")
    
    # validate_input 함수 벤치마크
    start_time = time.time()
    for _ in range(100):
        validate_input(sample_data)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    print(f"validate_input 평균 실행 시간: {avg_time:.4f}초")


def generate_test_report():
    """테스트 보고서 생성 - 사용되지 않음 (DEAD CODE)"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'test_summary': {
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0
        },
        'coverage': {
            'lines_covered': 0,
            'total_lines': 0,
            'percentage': 0.0
        },
        'performance_metrics': {
            'avg_execution_time': 0.0,
            'memory_usage': 0.0
        }
    }
    
    # 실제 보고서 생성 로직은 구현되지 않음
    print("테스트 보고서 생성 기능은 구현되지 않았습니다.")
    return report


def cleanup_test_files():
    """테스트 파일 정리 - 사용되지 않음 (DEAD CODE)"""
    import os
    
    test_files = [
        'test_output.txt',
        'test_report.json',
        'benchmark_results.csv',
        'performance_log.txt',
        'coverage_report.html',
        'temp_test_data.json'
    ]
    
    cleaned_files = 0
    for filename in test_files:
        if os.path.exists(filename):
            try:
                os.remove(filename)
                cleaned_files += 1
                print(f"삭제됨: {filename}")
            except Exception as e:
                print(f"삭제 실패 ({filename}): {e}")
    
    print(f"정리 완료: {cleaned_files}개 파일 삭제")
    return cleaned_files


def validate_test_environment():
    """테스트 환경 검증 - 사용되지 않음 (DEAD CODE)"""
    import sys
    import platform
    
    print("=== 테스트 환경 검증 ===")
    print(f"Python 버전: {sys.version}")
    print(f"플랫폼: {platform.platform()}")
    print(f"아키텍처: {platform.architecture()}")
    
    # 필요한 모듈 확인
    required_modules = ['unittest', 'json', 'datetime', 're', 'hashlib']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} 모듈 사용 가능")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} 모듈 누락")
    
    if missing_modules:
        print(f"누락된 모듈: {missing_modules}")
        return False
    else:
        print("모든 필수 모듈이 사용 가능합니다.")
        return True


def setup_test_data():
    """테스트 데이터 설정 - 사용되지 않음 (DEAD CODE)"""
    import json
    
    test_datasets = {
        'small_dataset': [
            {'id': 'small_001', 'name': '작은 데이터 1', 'value': 10},
            {'id': 'small_002', 'name': '작은 데이터 2', 'value': 20}
        ],
        'medium_dataset': [],
        'large_dataset': []
    }
    
    # 중간 크기 데이터셋 생성
    for i in range(100):
        test_datasets['medium_dataset'].append({
            'id': f'medium_{i:03d}',
            'name': f'중간 데이터 {i}',
            'value': i * 10
        })
    
    # 큰 데이터셋 생성
    for i in range(10000):
        test_datasets['large_dataset'].append({
            'id': f'large_{i:05d}',
            'name': f'큰 데이터 {i}',
            'value': i * 100
        })
    
    # 파일로 저장
    try:
        with open('test_datasets.json', 'w', encoding='utf-8') as f:
            json.dump(test_datasets, f, indent=2, ensure_ascii=False)
        print("테스트 데이터셋 생성 완료: test_datasets.json")
        return True
    except Exception as e:
        print(f"테스트 데이터셋 생성 실패: {e}")
        return False


def run_stress_tests():
    """스트레스 테스트 실행 - 사용되지 않음 (DEAD CODE)"""
    print("=== 스트레스 테스트 실행 ===")
    
    # 매우 큰 데이터셋으로 테스트
    stress_data = []
    for i in range(50000):
        stress_data.append({
            'id': f'stress_{i:06d}',
            'name': f'스트레스 테스트 데이터 {i}',
            'value': i * 7 + (i % 13) * 3
        })
    
    print(f"스트레스 테스트 데이터 크기: {len(stress_data)}")
    
    # 메모리 사용량 측정
    import sys
    initial_memory = sys.getsizeof(stress_data)
    print(f"초기 메모리 사용량: {initial_memory:,} bytes")
    
    # 처리 시간 측정
    start_time = time.time()
    try:
        processed_data = process_data(stress_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        final_memory = sys.getsizeof(processed_data)
        
        print(f"처리 시간: {processing_time:.2f}초")
        print(f"최종 메모리 사용량: {final_memory:,} bytes")
        print(f"처리된 데이터 수: {len(processed_data)}")
        
        return True
    except Exception as e:
        print(f"스트레스 테스트 실패: {e}")
        return False


def duplicate_test_runner():
    """중복된 테스트 실행기 - 사용되지 않음 (DEAD CODE)"""
    # run_basic_tests()와 거의 동일한 로직
    print("=== 중복 테스트 실행기 ===")
    
    suite = unittest.TestSuite()
    
    # 같은 테스트들을 다시 추가
    suite.addTest(TestDataProcessor('test_process_data_valid_input'))
    suite.addTest(TestDataProcessor('test_validate_input_valid_data'))
    suite.addTest(TestUtilityFunctions('test_string_operations'))
    
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    print(f"중복 테스트 실행 결과: {result.testsRun}개 테스트")
    return result.wasSuccessful()


def run_tests():
    """메인 테스트 실행 함수 - 자주 호출됨"""
    print("테스트 시작...")
    
    try:
        # 기본 테스트만 실행
        success = run_basic_tests()
        
        if success:
            print("✓ 모든 기본 테스트가 통과했습니다.")
        else:
            print("✗ 일부 테스트가 실패했습니다.")
        
        return success
        
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {e}")
        return False


# 메인 실행 부분
if __name__ == "__main__":
    print("=== 테스트 러너 독립 실행 ===")
    
    # 명령행 인자 처리
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--extended":
            success = run_extended_tests()
        elif command == "--performance":
            success = run_performance_tests()
        elif command == "--legacy":
            success = run_legacy_tests()
        elif command == "--stress":
            success = run_stress_tests()
        elif command == "--setup":
            success = setup_test_data()
        elif command == "--cleanup":
            cleanup_test_files()
            success = True
        elif command == "--validate":
            success = validate_test_environment()
        else:
            print(f"알 수 없는 명령: {command}")
            print("사용 가능한 명령: --extended, --performance, --legacy, --stress, --setup, --cleanup, --validate")
            success = False
    else:
        # 기본 테스트 실행
        success = run_tests()
    
    # 결과에 따른 종료 코드
    sys.exit(0 if success else 1)