#!/usr/bin/env python3
"""
Neo4j Connection Test Script
"""

from db_manager import Neo4jManager
import sys

def test_neo4j_connection():
    print('🔌 Neo4j 연결 테스트 중...')
    
    # Use the updated credentials
    manager = Neo4jManager(
        uri='bolt://localhost:7687', 
        username='neo4j', 
        password='codycody'
    )

    if manager.connect():
        print('✅ Neo4j 연결 성공!')
        
        # Clear and test basic operations
        if manager.clear_database():
            print('✅ 데이터베이스 초기화 성공!')
        
        # Test with sample data
        sample_nodes = [
            {
                'id': 'test.py:main', 
                'type': 'function', 
                'file': 'test.py', 
                'label': 'main', 
                'dead': False
            }
        ]
        sample_edges = []
        
        if manager.store_analysis_results(sample_nodes, sample_edges):
            print('✅ 샘플 데이터 저장 성공!')
        
        # Get graph data
        graph_data = manager.get_graph_data()
        print(f'✅ 그래프 데이터 조회 성공: {len(graph_data["nodes"])}개 노드')
        
        # Get statistics
        stats = manager.get_statistics()
        print(f'✅ 통계 조회 성공: 총 {stats.get("total_nodes", 0)}개 노드')
        
        manager.close()
        print('✅ 모든 Neo4j 테스트 완료!')
        return True
        
    else:
        print('❌ Neo4j 연결 실패!')
        print('다음을 확인해주세요:')
        print('1. Neo4j Desktop이 실행 중인가요?')
        print('2. 데이터베이스 "cody"가 시작되었나요?')
        print('3. 포트 7687이 열려있나요?')
        print('4. 패스워드가 "codycody"로 설정되었나요?')
        return False

if __name__ == "__main__":
    success = test_neo4j_connection()
    if not success:
        sys.exit(1)
