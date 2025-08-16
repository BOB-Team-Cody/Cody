# 🕸️ Code Weaver

**정적 코드 분석과 Dead Code 탐지를 통한 3D 코드 시각화 도구**

Code Weaver는 Python 프로젝트를 분석하여 함수/클래스 간의 호출 관계를 추출하고, 사용되지 않는 코드(dead code)를 탐지하여 Neo4j 그래프 데이터베이스에 저장한 후 3D로 시각화하는 도구입니다.

## ✨ 주요 기능

- **🔍 정적 코드 분석**: AST를 이용한 Python 코드 구조 분석
- **💀 Dead Code 탐지**: vulture를 이용한 사용되지 않는 코드 식별
- **📊 그래프 데이터베이스**: Neo4j를 이용한 코드 관계 저장
- **🌐 REST API**: FastAPI 기반 분석 및 데이터 제공 API
- **📈 시각화 지원**: Three.js용 그래프 데이터 제공

## 🏗️ 기술 스택

- **분석 엔진**: Python 3.9+ (ast, vulture)
- **데이터베이스**: Neo4j
- **API 서버**: FastAPI + uvicorn
- **데이터 검증**: Pydantic

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd code-weaver

# 의존성 설치
pip install -e .
```

### 2. Neo4j 설정

Neo4j를 로컬에 설치하거나 Docker로 실행하세요:

```bash
# Docker로 Neo4j 실행
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 3. 서버 실행

```bash
# 개발 서버 실행
python main.py

# 또는 uvicorn으로 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. API 사용

서버가 실행되면 `http://localhost:8000`에서 API를 사용할 수 있습니다.

#### 프로젝트 분석

```bash
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"path": "/path/to/your/python/project"}'
```

#### 그래프 데이터 조회

```bash
curl "http://localhost:8000/graph-data"
```

## 📡 API 엔드포인트

### `POST /analyze`

Python 프로젝트를 분석하고 결과를 Neo4j에 저장합니다.

**요청:**
```json
{
  "path": "/path/to/python/project"
}
```

**응답:**
```json
{
  "success": true,
  "message": "Analysis completed successfully",
  "nodes_count": 150,
  "edges_count": 89,
  "statistics": {...}
}
```

### `GET /graph-data`

Three.js 시각화용 그래프 데이터를 반환합니다.

**응답:**
```json
{
  "nodes": [
    {
      "id": "module.py:function_name",
      "name": "function_name",
      "file": "module.py",
      "type": "function",
      "dead": false,
      "callCount": 5,
      "size": 25
    }
  ],
  "links": [
    {
      "source": "caller_id",
      "target": "callee_id"
    }
  ]
}
```

### `GET /statistics`

분석 통계 정보를 반환합니다.

### `GET /health`

서비스 상태를 확인합니다.

### `DELETE /clear`

데이터베이스의 모든 데이터를 삭제합니다.

## ⚙️ 환경 변수 설정

```bash
# Neo4j 연결 설정
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS 설정
CORS_ORIGINS=*
```

## 🎨 시각화 규칙

분석 결과는 다음과 같이 시각화됩니다:

- **📏 노드 크기**: 호출 횟수에 비례 (많이 호출될수록 큰 노드)
- **💀 Dead Code**: 연결이 없는 단독 노드로 표시
- **🔗 연결선**: 함수 간 호출 관계를 나타냄

## 📁 프로젝트 구조

```
code-weaver/
├── analyzer.py       # 정적 코드 분석기
├── db_manager.py     # Neo4j 데이터베이스 매니저
├── main.py          # FastAPI 서버
├── config.py        # 설정 관리
├── pyproject.toml   # 프로젝트 의존성
└── README.md        # 프로젝트 문서
```

## 🔧 개발 및 테스트

### 분석기 단독 테스트

```bash
python analyzer.py /path/to/test/project
```

### 데이터베이스 매니저 테스트

```bash
python db_manager.py
```

### API 문서 확인

서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI를 통해 API 문서를 확인할 수 있습니다.

## 🤝 기여하기

1. 이 저장소를 포크하세요
2. 기능 브랜치를 생성하세요 (`git checkout -b feature/AmazingFeature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/AmazingFeature`)
5. Pull Request를 생성하세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 🙋‍♂️ 지원

문제가 있거나 질문이 있으시면 Issue를 생성해 주세요.
