
# Network RAG System Project Purpose

## Overview
Network RAG Systemは、Retrieval-Augmented Generation（RAG）技術を活用したネットワーク装置のコンフィグレーション自動生成システムです。初心者でも簡単に使えるように設計されており、事前に定義された知識ベース（KB）を活用して、一貫性のある高品質なネットワークコンフィグを自動生成します。

## 主な機能
- **自然言語で設定生成**: 「R1の基本設定を生成して」のような簡単な言葉でコンフィグが生成できます
- **関連情報の自動検索**: クエリに基づいて関連するデバイス、ポリシー、テンプレートを自動的に検索
- **テンプレート変数置換**: `{{hostname}}` のような変数を自動的に置換して実際の設定を生成
- **検証機能**: 生成されたコンフィグの構文をチェックしてエラーを検出
- **日本語対応**: 日本語のクエリにも対応した日本語ネットワーク環境に最適化

## ターゲットユーザー
- ネットワークエンジニア
- システム管理者
- ネットワーク設計者
- DevOpsエンジニア

## 使用例
```python
from src.rag_system import NetworkRAGSystem
from src.config_generator import NetworkConfigGenerator

# システムを初期化
rag_system = NetworkRAGSystem()
config_generator = NetworkConfigGenerator()

# クエリを入力
query = "R1の基本設定を生成して"

# コンフィグを自動生成
generated_config = config_generator.generate_config(query)
```
