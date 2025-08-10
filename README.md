# Network RAG System

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Network RAG Systemは、Retrieval-Augmented Generation（RAG）技術を活用したネットワーク装置のコンフィグレーション自動生成システムです。事前に定義された知識ベース（KB）を活用して、一貫性のある高品質なネットワークコンフィグを自動生成します。

## 🚀 主な特徴

- **知識ベースの一元管理**: ネットワークポリシー、デバイス設定、テンプレートなどを一元管理
- **関連情報の自動検索**: クエリに基づいて関連情報を自動的に検索・抽出
- **コンフィグの自動生成**: ポリシーと要件に基づいてコンフィグを自動生成
- **検証機能**: 生成されたコンフィグの構文検証とビジネスルール検証
- **バージョン管理**: 変更履歴とバックアップ機能
- **ワークフロー連携**: digdagなどのCI/CDツールとの連携

## 📦 インストール

### 基本的なインストール
```bash
git clone https://github.com/kaishin0527/network-rag-system.git
cd network-rag-system
pip install -r requirements/base.txt
```

### 開発環境のセットアップ
```bash
git clone https://github.com/kaishin0527/network-rag-system.git
cd network-rag-system
pip install -r requirements/dev.txt
pre-commit install
```

## 🚀 クイックスタート

### 基本的な使用例
```python
from src.rag_system import NetworkRAGSystem
from src.config_generator import NetworkConfigGenerator

# RAGシステムの初期化
rag_system = NetworkRAGSystem()
config_generator = NetworkConfigGenerator()

# クエリの定義
query = "R1に新しい支社Cの接続を追加してOSPFで設定してください"

# コンフィグの生成
generated_config = config_generator.generate_config(query)

# 結果の表示
print(f"デバイス: {generated_config.device_name}")
print(f"設定タイプ: {generated_config.config_type}")
print("生成されたコンフィグ:")
print(generated_config.config_content)
```

### バッチ処理の例
```python
from src.config_generator import NetworkConfigGenerator

# コンフィグ生成器の初期化
config_generator = NetworkConfigGenerator()

# バッチ処理用クエリリスト
batch_queries = [
    "R1に支社C接続を追加",
    "SW1にVLAN40を追加",
    "R2にセキュリティ設定を強化"
]

# バッチ処理の実行
for query in batch_queries:
    config = config_generator.generate_config(query)
    print(f"✓ {query}: {config.device_name}")
```

## 📁 ディレクトリ構成

```
network-rag-system/
├── .github/                    # GitHub関連ファイル
├── docs/                       # ドキュメント
├── knowledge-base/             # 知識ベース（KB）
│   ├── devices/               # デバイスポリシー
│   ├── routing/               # ルーティングポリシー
│   ├── security/              # セキュリティポリシー
│   └── automation/            # 自動化設定
├── src/                       # ソースコード
│   ├── rag_system.py          # RAGシステム本体
│   ├── config_generator.py    # コンフィグ生成器
│   ├── knowledge_base.py      # 知識ベース管理
│   └── utils.py               # ユーティリティ
├── examples/                  # 使用例
├── tests/                     # テスト
├── requirements/              # 依存関係
└── README.md                  # このファイル
```

## 🔧 構成要件

- Python 3.8+
- PyYAML>=6.0
- markdown>=3.4.3
- pathlib2>=2.3.7
- typing-extensions>=4.8.0

## 📖 ドキュメント

- [📖 ドキュメント](docs/README.md)
- [🔌 APIリファレンス](docs/API.md)
- [💡 使用例](docs/EXAMPLES.md)
- [🤝 貢献ガイド](docs/CONTRIBUTING.md)

## 🧪 テスト

```bash
# 全てのテストを実行
pytest tests/

# カバレッジ付きでテストを実行
pytest tests/ --cov=src --cov-report=html

# 特定のテストを実行
pytest tests/test_rag_system.py
```

## 🚀 開発

### 環境のセットアップ
```bash
# 依存関係のインストール
pip install -r requirements/dev.txt

# プレコミットフックの設定
pre-commit install

# テストの実行
./scripts/test.sh
```

### コードのフォーマット
```bash
# コードフォーマット
black src/ examples/ tests/

# インポートの整理
isort src/ examples/ tests/

# リントチェック
flake8 src/ examples/ tests/
```

## 🤝 貢献

貢献歓迎！詳細は[貢献ガイド](docs/CONTRIBUTING.md)を参照してください。

## 📄 ライセンス

このプロジェクトは[MITライセンス](LICENSE)の下で提供されています。

## 🙏 クレジット

このプロジェクトは、ネットワーク運用の自動化と効率化を目指して開発されました。

## 📞 お問い合わせ

- 📧 Email: team@network-rag.com
- 🐛 Issues: [GitHub Issues](https://github.com/kaishin0527/network-rag-system/issues)
- 📖 Documentation: [GitHub Pages](https://kaishin0527.github.io/network-rag-system)
