
#!/usr/bin/env python3
# test_openhands_mock.py
import sys
import os
sys.path.append('/workspace/network-rag-system')

# OpenHandsをモック
class MockAgent:
    def __init__(self, *args, **kwargs):
        pass
    
    def run(self, *args, **kwargs):
        return {"result": "mock_result"}

class MockOpenHands:
    Agent = MockAgent

# モックをsys.modulesに登録
sys.modules['openhands'] = MockOpenHands()
sys.modules['openhands.core'] = MockOpenHands()
sys.modules['openhands.core.agent'] = MockOpenHands()

# これで通常のテストを実行できる
from src.openhands_integration import OpenHandsIntegration
from src.llm_integration import GenerationRequest

def test_openhands_integration():
    """OpenHands統合テスト"""
    print("=== OpenHands Integration Test ===\n")
    
    try:
        # OpenHands統合の初期化
        openhands_integration = OpenHandsIntegration()
        print("✓ OpenHands Integration initialized")
        
        # テストリクエスト
        request = GenerationRequest(
            query="R1の基本設定を生成して",
            device_name="R1",
            config_type="basic"
        )
        
        # コンフィグ生成
        result = openhands_integration.generate_network_config(request)
        print(f"✓ Config generated for {result['device_name']}")
        print(f"  Config Type: {result['config_type']}")
        print(f"  Validation: {result['validation_result']['is_valid']}")
        print(f"  Content Length: {len(result['config_content'])} characters")
        
        # バッチ処理テスト
        requests = [
            GenerationRequest("R2のOSPF設定", "R2", "routing"),
            GenerationRequest("SW1のVLAN設定", "SW1", "switching")
        ]
        
        batch_results = []
        for req in requests:
            batch_result = openhands_integration.generate_network_config(req)
            batch_results.append(batch_result)
            print(f"✓ Batch config generated for {batch_result['device_name']}")
        
        print(f"\nBatch Results:")
        print(f"  Total: {len(batch_results)}")
        print(f"  Successful: {sum(1 for r in batch_results if r['validation_result']['is_valid'])}")
        
        print("\n✓ OpenHands Integration Test Completed")
        return True
        
    except Exception as e:
        print(f"✗ OpenHands Integration Test Failed: {e}")
        return False

def test_configuration():
    """設定ファイルテスト"""
    print("\n=== Configuration Test ===\n")
    
    try:
        from src.llm_integration import LLMIntegration
        
        # 設定ファイルの読み込み
        llm_integration = LLMIntegration()
        config = llm_integration.config
        
        print("✓ Configuration loaded")
        print(f"  LLM Config: {config.get('llm', {})}")
        
        # プロバイダー情報
        providers = llm_integration.get_available_providers()
        print(f"  Available Providers: {len(providers)}")
        for provider in providers:
            print(f"    - {provider['display_name']}: {provider['enabled']}")
        
        print("\n✓ Configuration Test Completed")
        return True
        
    except Exception as e:
        print(f"✗ Configuration Test Failed: {e}")
        return False

def main():
    """メインテスト関数"""
    print("Network RAG System - OpenHands Integration Tests (Mock)")
    print("=" * 60)
    
    # OpenHands統合テスト
    openhands_success = test_openhands_integration()
    
    # 設定テスト
    config_success = test_configuration()
    
    print("\n" + "=" * 60)
    if openhands_success and config_success:
        print("✓ All tests completed successfully!")
    else:
        print("✗ Some tests failed")
    
    return openhands_success and config_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
