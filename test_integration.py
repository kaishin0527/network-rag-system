#!/usr/bin/env python3
# test_integration.py
import sys
import os
sys.path.append('/workspace/network-rag-system')

from src.openhands_integration import OpenHandsIntegration
from src.llm_integration import LLMIntegration, GenerationRequest
from src.llm_client import LLMConfig, LLMProvider

def test_basic_functionality():
    """基本的な機能テスト"""
    print("=== Basic Integration Test ===\n")
    
    # 1. OpenHands Integrationテスト
    print("1. Testing OpenHands Integration...")
    try:
        openhands_integration = OpenHandsIntegration()
        result = openhands_integration.process_single_query("R1の基本設定を生成して")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Device: {result.get('device_name', 'Unknown')}")
        print(f"   Config Type: {result.get('config_type', 'Unknown')}")
        print("   ✓ OpenHands Integration working")
    except Exception as e:
        print(f"   ✗ OpenHands Integration failed: {e}")
    
    # 2. LLM Integrationテスト
    print("\n2. Testing LLM Integration...")
    try:
        llm_integration = LLMIntegration()
        request = GenerationRequest(
            query="R1の基本設定を生成して",
            device_name="R1",
            config_type="basic"
        )
        result = llm_integration.generate_network_config(request)
        print(f"   Status: {result['validation_result']['is_valid']}")
        print(f"   Device: {result['device_name']}")
        print(f"   Config Type: {result['config_type']}")
        print("   ✓ LLM Integration working")
    except Exception as e:
        print(f"   ✗ LLM Integration failed: {e}")
    
    # 3. プロバイダー切り替えテスト
    print("\n3. Testing Provider Switching...")
    try:
        llm_integration = LLMIntegration()
        providers = llm_integration.get_available_providers()
        print(f"   Available providers: {len(providers)}")
        for provider in providers:
            print(f"   - {provider['display_name']}: {provider['enabled']}")
        print("   ✓ Provider information available")
    except Exception as e:
        print(f"   ✗ Provider switching test failed: {e}")
    
    # 4. 統計テスト
    print("\n4. Testing Statistics...")
    try:
        openhands_integration = OpenHandsIntegration()
        openhands_stats = openhands_integration.get_statistics()
        print(f"   OpenHands Stats: {openhands_stats}")
        
        llm_integration = LLMIntegration()
        llm_stats = llm_integration.get_generation_statistics()
        print(f"   LLM Stats: {llm_stats}")
        print("   ✓ Statistics working")
    except Exception as e:
        print(f"   ✗ Statistics test failed: {e}")
    
    print("\n=== Basic Test Completed ===")

def test_config_generation():
    """コンフィグ生成テスト"""
    print("\n=== Config Generation Test ===\n")
    
    try:
        llm_integration = LLMIntegration()
        
        # 各種設定タイプのテスト
        test_cases = [
            ("R1の基本設定を生成して", "R1", "basic"),
            ("SW1のVLAN設定を追加して", "SW1", "switching"),
            ("R2のOSPF設定を構成してください", "R2", "routing"),
            ("R3のセキュリティ設定を強化してください", "R3", "security"),
            ("R4の監視設定を追加してください", "R4", "monitoring")
        ]
        
        for query, device, config_type in test_cases:
            print(f"Testing: {query}")
            
            request = GenerationRequest(
                query=query,
                device_name=device,
                config_type=config_type
            )
            
            result = llm_integration.generate_network_config(request)
            
            if result['validation_result']['is_valid']:
                print(f"   ✓ Generated config for {device} ({config_type})")
                print(f"     Length: {len(result['config_content'])} characters")
                print(f"     Preview: {result['config_content'][:80]}...")
            else:
                print(f"   ✗ Failed to generate config for {device}")
                print(f"     Error: {result['validation_result'].get('error', 'Unknown')}")
            
            print()
        
        print("=== Config Generation Test Completed ===")
        
    except Exception as e:
        print(f"✗ Config generation test failed: {e}")

def test_batch_processing():
    """バッチ処理テスト"""
    print("\n=== Batch Processing Test ===\n")
    
    try:
        openhands_integration = OpenHandsIntegration()
        
        queries = [
            "R1の基本設定を生成して",
            "SW1のVLAN設定を追加して",
            "R2のOSPF設定を構成してください"
        ]
        
        print("Processing batch queries...")
        results = []
        for i, query in enumerate(queries, 1):
            print(f"  {i}. {query}")
            result = openhands_integration.process_single_query(query)
            results.append(result)
            print(f"     Status: {result.get('status', 'Unknown')}")
        
        # 統計の表示
        stats = openhands_integration.get_statistics()
        print(f"\nBatch Processing Results:")
        print(f"  Total: {stats['total_tasks']}")
        print(f"  Completed: {stats['completed_tasks']}")
        print(f"  Failed: {stats['failed_tasks']}")
        print(f"  Success Rate: {stats['success_rate']:.2%}")
        
        print("\n=== Batch Processing Test Completed ===")
        
    except Exception as e:
        print(f"✗ Batch processing test failed: {e}")

def main():
    """メインテスト関数"""
    print("Network RAG System - Integration Tests")
    print("=" * 50)
    
    # 基本的な機能テスト
    test_basic_functionality()
    
    # コンフィグ生成テスト
    test_config_generation()
    
    # バッチ処理テスト
    test_batch_processing()
    
    print("\n" + "=" * 50)
    print("All tests completed!")

if __name__ == "__main__":
    main()




