


#!/usr/bin/env python3
# basic_usage.py
import sys
import os
sys.path.append('/workspace/network-rag-system')

from src.rag_system import NetworkRAGSystem
from src.config_generator import NetworkConfigGenerator
from src.knowledge_base import KnowledgeBase

def main():
    print("=== Network RAG System - Basic Usage Example ===\n")
    
    # RAGシステムの初期化
    rag_system = NetworkRAGSystem()
    
    # コンフィグ生成器の初期化
    config_generator = NetworkConfigGenerator()
    
    # クエリの定義
    queries = [
        "R1に新しい支社Cの接続を追加してOSPFで設定してください",
        "SW1にVLAN40を追加して開発部用に設定してください",
        "R2のセキュリティを強化してACLを追加してください",
        "両方のルータに監視設定を追加してください"
    ]
    
    # 各クエリの処理
    for i, query in enumerate(queries, 1):
        print(f"--- Query {i}: {query} ---")
        
        # 関連情報の検索
        relevant_info = rag_system.retrieve_relevant_info(query)
        print(f"Relevant devices: {relevant_info['relevant_devices']}")
        print(f"Relevant policies: {relevant_info['relevant_policies']}")
        print(f"Relevant templates: {relevant_info['relevant_templates']}")
        
        # コンフィグの生成
        generated_config = config_generator.generate_config(query)
        
        # 生成結果の表示
        print(f"\nGenerated Config for {generated_config.device_name}:")
        print("-" * 50)
        print(generated_config.config_content)
        print("-" * 50)
        
        # 検証結果の表示
        validation_result = generated_config.validation_result
        print(f"Validation Result: {'PASS' if validation_result['is_valid'] else 'FAIL'}")
        if validation_result['errors']:
            print(f"Errors: {validation_result['errors']}")
        if validation_result['warnings']:
            print(f"Warnings: {validation_result['warnings']}")
        
        # メタデータの表示
        metadata = generated_config.metadata
        print(f"Metadata: {metadata}")
        
        print("\n" + "="*70 + "\n")
    
    # 生成されたコンフィグの保存
    print("--- Saving Generated Configs ---")
    for config in config_generator.get_generated_configs():
        filepath, validation_filepath = config_generator.save_config(config)
        print(f"Config saved to: {filepath}")
        print(f"Validation saved to: {validation_filepath}")
    
    print("\n=== Basic Usage Example Completed ===")

if __name__ == "__main__":
    main()




