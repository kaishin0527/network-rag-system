



#!/usr/bin/env python3
# openhands_llm_integration_example.py
import asyncio
import sys
import os
sys.path.append('/workspace/network-rag-system')

from src.openhands_integration import OpenHandsIntegration
from src.llm_integration import LLMIntegration, GenerationRequest
from datetime import datetime

def main():
    """メイン関数"""
    print("=== OpenHands + LLM Integration Example ===\n")
    
    # OpenHands統合の初期化
    try:
        openhands_integration = OpenHandsIntegration()
        print("✓ OpenHands Integration initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize OpenHands Integration: {e}")
        openhands_integration = None
    
    # LLM統合の初期化
    try:
        llm_integration = LLMIntegration()
        print("✓ LLM Integration initialized successfully")
        print(f"  - Provider: {llm_integration.client.get_provider_info()['provider']}")
        print(f"  - Model: {llm_integration.client.get_provider_info()['model']}")
    except Exception as e:
        print(f"✗ Failed to initialize LLM Integration: {e}")
        llm_integration = None
    
    # クエリの定義
    queries = [
        "R1の基本設定を生成して",
        "SW1にVLAN40を追加して開発部用に設定してください",
        "R2のセキュリティを強化してACLを追加してください",
        "R1のOSPF設定を構成してください",
        "SW1の監視設定を追加してください"
    ]
    
    print("\n--- OpenHands Integration Test ---")
    if openhands_integration:
        # OpenHandsでのバッチ処理
        try:
            openhands_results = []
            for i, query in enumerate(queries, 1):
                print(f"\nProcessing query {i}: {query}")
                result = openhands_integration.process_single_query(query)
                openhands_results.append(result)
                
                print(f"Status: {result.get('status', 'Unknown')}")
                if result.get('status') == 'completed':
                    print(f"Device: {result.get('device_name', 'Unknown')}")
                    print(f"Config Type: {result.get('config_type', 'Unknown')}")
                    print(f"Config Preview: {result.get('config_content', '')[:100]}...")
                    print(f"Valid: {result.get('validation_result', {}).get('is_valid', False)}")
                else:
                    print(f"Error: {result.get('error', 'Unknown error')}")
                
                print("-" * 50)
            
            # 統計の表示
            openhands_stats = openhands_integration.get_statistics()
            print(f"\nOpenHands Statistics:")
            print(f"  Total Tasks: {openhands_stats['total_tasks']}")
            print(f"  Completed: {openhands_stats['completed_tasks']}")
            print(f"  Failed: {openhands_stats['failed_tasks']}")
            print(f"  Success Rate: {openhands_stats['success_rate']:.2%}")
            
        except Exception as e:
            print(f"✗ OpenHands processing failed: {e}")
    else:
        print("✗ OpenHands Integration not available")
    
    print("\n--- LLM Integration Test ---")
    if llm_integration:
        # LLMでの個別処理
        try:
            for i, query in enumerate(queries, 1):
                print(f"\nProcessing query {i}: {query}")
                
                request = GenerationRequest(
                    query=query,
                    device_name=f"Device{i}",
                    config_type="general"
                )
                
                result = llm_integration.generate_network_config(request)
                
                print(f"Device: {result['device_name']}")
                print(f"Config Type: {result['config_type']}")
                print(f"Valid: {result['validation_result']['is_valid']}")
                
                if result['validation_result']['is_valid']:
                    print(f"Config Preview: {result['config_content'][:100]}...")
                else:
                    print(f"Error: {result['validation_result'].get('error', 'Unknown error')}")
                
                print("-" * 50)
            
            # 統計の表示
            llm_stats = llm_integration.get_generation_statistics()
            print(f"\nLLM Statistics:")
            print(f"  Total Requests: {llm_stats['total']}")
            print(f"  Successful: {llm_stats['success']}")
            print(f"  Failed: {llm_stats['failed']}")
            print(f"  Success Rate: {llm_stats['success_rate']:.2%}")
            
            if 'provider_statistics' in llm_stats:
                print(f"\nProvider Statistics:")
                for provider, stats in llm_stats['provider_statistics'].items():
                    print(f"  {provider}: {stats['success']}/{stats['total']} ({stats['success']/stats['total']:.2%})")
            
        except Exception as e:
            print(f"✗ LLM processing failed: {e}")
    else:
        print("✗ LLM Integration not available")
    
    print("\n--- Combined Integration Test ---")
    if openhands_integration and llm_integration:
        try:
            # 統合テスト
            test_query = "R1の基本設定を生成して"
            
            print(f"\nTest Query: {test_query}")
            
            # OpenHandsで処理
            openhands_result = openhands_integration.process_single_query(test_query)
            print(f"OpenHands Result: {openhands_result.get('status', 'Unknown')}")
            
            # LLMで処理
            llm_request = GenerationRequest(
                query=test_query,
                device_name="R1",
                config_type="basic"
            )
            llm_result = llm_integration.generate_network_config(llm_request)
            print(f"LLM Result: {llm_result['validation_result']['is_valid']}")
            
            # 結果の比較
            if openhands_result.get('status') == 'completed' and llm_result['validation_result']['is_valid']:
                print("✓ Both integrations working correctly")
            else:
                print("✗ Some integrations have issues")
                
        except Exception as e:
            print(f"✗ Combined integration test failed: {e}")
    
    print("\n--- Results Summary ---")
    if openhands_integration:
        openhands_stats = openhands_integration.get_statistics()
        print(f"OpenHands: {openhands_stats['completed_tasks']}/{openhands_stats['total_tasks']} successful")
    
    if llm_integration:
        llm_stats = llm_integration.get_generation_statistics()
        print(f"LLM Integration: {llm_stats['success']}/{llm_stats['total']} successful")
    
    print("\n=== Integration Example Completed ===")

if __name__ == "__main__":
    main()




