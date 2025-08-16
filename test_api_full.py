#!/usr/bin/env python3
"""
API Test Script for Code Weaver
"""

import requests
import json
import time

API_BASE = 'http://127.0.0.1:8000'

def test_api():
    print("🚀 Code Weaver API 테스트 시작...")
    
    try:
        # 1. Health Check
        print("\n1️⃣ Health Check...")
        response = requests.get(f'{API_BASE}/health', timeout=5)
        print(f"   Status: {response.status_code}")
        health_data = response.json()
        print(f"   Health: {health_data}")
        
        # 2. Analyze Project
        print("\n2️⃣ 프로젝트 분석...")
        analyze_data = {"path": "sample_project"}
        response = requests.post(f'{API_BASE}/analyze', json=analyze_data, timeout=30)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            analysis_result = response.json()
            print(f"   ✅ 분석 성공!")
            print(f"   📊 노드: {analysis_result['nodes_count']}개")
            print(f"   🔗 엣지: {analysis_result['edges_count']}개")
        else:
            print(f"   ❌ 분석 실패: {response.text}")
            return
        
        # 3. Get Graph Data
        print("\n3️⃣ 그래프 데이터 조회...")
        response = requests.get(f'{API_BASE}/graph-data', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            graph_data = response.json()
            print(f"   ✅ 그래프 데이터 조회 성공!")
            print(f"   🌟 노드: {len(graph_data['nodes'])}개")
            print(f"   🔗 링크: {len(graph_data['links'])}개")
            
            # Show sample nodes
            print(f"\n   📋 샘플 노드 (처음 5개):")
            for i, node in enumerate(graph_data['nodes'][:5]):
                dead_marker = "💀" if node.get('dead', False) else "✅"
                call_count = node.get('callCount', 0)
                print(f"      {i+1}. {dead_marker} {node['name']} ({node['type']}) - 호출: {call_count}회")
            
            # Count dead code
            dead_nodes = [n for n in graph_data['nodes'] if n.get('dead', False)]
            print(f"\n   💀 Dead Code 발견: {len(dead_nodes)}개")
            for node in dead_nodes:
                print(f"      - {node['name']} ({node['file']})")
                
        else:
            print(f"   ❌ 그래프 데이터 조회 실패: {response.text}")
        
        # 4. Get Statistics
        print("\n4️⃣ 통계 조회...")
        response = requests.get(f'{API_BASE}/statistics', timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 통계 조회 성공!")
            print(f"   📊 전체 통계:")
            print(f"      - 총 노드: {stats.get('total_nodes', 0)}개")
            print(f"      - 총 관계: {stats.get('total_relationships', 0)}개")
            print(f"      - Dead Code: {stats.get('dead_code_count', 0)}개")
            
            if 'most_called' in stats and stats['most_called']:
                print(f"   🔥 최다 호출 함수:")
                for i, func in enumerate(stats['most_called'][:3]):
                    print(f"      {i+1}. {func['name']} - {func['callCount']}회")
        
        print(f"\n🎉 모든 API 테스트 완료! 프론트엔드에서 사용할 준비가 되었습니다.")
        
    except requests.exceptions.ConnectionError:
        print("❌ API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_api()
