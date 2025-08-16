# Code Weaver - 실행 가이드

## 🚀 현재 상태

프로젝트가 성공적으로 구현되었습니다!

### ✅ 작동하는 기능들:
- ✅ 정적 코드 분석기 (AST + vulture)
- ✅ Dead code 탐지
- ✅ FastAPI 서버 
- ✅ API 엔드포인트들
- ⚠️ Neo4j 연동 (Neo4j 설치 필요)

## 🔧 실행 방법

### 1. 가상환경 활성화
```powershell
.\.cody\Scripts\activate
```

### 2. 서버 시작
```powershell
C:/Users/panma/Cody/.cody/Scripts/python.exe main.py
```

### 3. 브라우저에서 확인
- API 문서: http://127.0.0.1:8000/docs
- 기본 엔드포인트: http://127.0.0.1:8000/

### 4. 분석 테스트
```powershell
# 직접 분석기 테스트
C:/Users/panma/Cody/.cody/Scripts/python.exe test_analyzer.py

# API 테스트 (서버 실행 후)
C:/Users/panma/Cody/.cody/Scripts/python.exe test_api.py
```

## 📊 테스트 결과

샘플 프로젝트 분석:
- **29개 노드** (함수, 클래스, 모듈)
- **37개 엣지** (호출 관계)
- **6개 Dead Code** 탐지

### 탐지된 Dead Code:
1. `main.py:dead_function_1` (function)
2. `main.py:dead_function_2` (function) 
3. `main.py:DeadClass` (class)
4. `test_runner.py:unused_test` (function)
5. `utils.py:unused_validator` (function)
6. `utils.py:standalone_function` (function)

## 🗄️ Neo4j 설정 (선택사항)

그래프 시각화를 위해 Neo4j를 설치하려면:

```powershell
# Docker로 Neo4j 실행
docker run --publish=7474:7474 --publish=7687:7687 --env NEO4J_AUTH=neo4j/password neo4j:latest
```

## 🎯 다음 단계

1. **Neo4j 연동**: 그래프 데이터베이스 설치 및 연결
2. **프론트엔드**: React + Three.js 3D 시각화
3. **개선사항**: 
   - 크로스 모듈 참조 분석
   - 더 정확한 호출 관계 추적
   - 대용량 프로젝트 최적화

## 🧪 API 엔드포인트

- `GET /` - 기본 정보
- `GET /health` - 서비스 상태
- `POST /analyze` - 프로젝트 분석
- `GET /graph-data` - 시각화 데이터
- `GET /statistics` - 통계 정보
- `DELETE /clear` - 데이터 초기화
