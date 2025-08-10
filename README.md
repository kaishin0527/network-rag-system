# Network RAG System

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Network RAG Systemは、Retrieval-Augmented Generation（RAG）技術を活用したネットワーク装置のコンフィグレーション自動生成システムです。事前に定義された知識ベース（KB）を活用して、一貫性のある高品質なネットワークコンフィグを自動生成します。**OpenHands連携機能**により、LLM APIと連携した高度な自動化を実現します。

## 🚀 主な特徴

- **知識ベースの一元管理**: ネットワークポリシー、デバイス設定、テンプレートなどを一元管理
- **関連情報の自動検索**: クエリに基づいて関連情報を自動的に検索・抽出
- **コンフィグの自動生成**: ポリシーと要件に基づいてコンフィグを自動生成
- **検証機能**: 生成されたコンフィグの構文検証とビジネスルール検証
- **バージョン管理**: 変更履歴とバックアップ機能
- **ワークフロー連携**: digdagなどのCI/CDツールとの連携
- **🤖 OpenHands連携**: LLM APIと連携した高度な自動化エージェント機能
- **🔄 バッチ処理**: 複数クエリの一括処理と結果管理
- **🌐 Web API**: RESTful APIによる外部システム連携

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

### OpenHands連携の例
```python
from network_rag_system_integration_example import OpenHandsNetworkAgent, OpenHandsIntegrationConfig

# OpenHands連携設定
config = OpenHandsIntegrationConfig(
    llm_api_url="http://localhost:8000",
    llm_api_key="your-api-key"
)

# エージェントの初期化
agent = OpenHandsNetworkAgent(config)

# クエリの処理
result = agent.process_network_request(
    query="R1に新しい支社Cの接続を追加してOSPFで設定してください",
    device_name="R1",
    config_type="ospf"
)

# 結果の表示
print(f"生成されたコンフィグ:\n{result['config_content']}")
print(f"検証結果: {'合格' if result['validation_result']['is_valid'] else '不合格'}")
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
├── network-rag-system-integration-example.py  # OpenHands連携サンプル
├── network-rag-system-integration-plan.md     # 連携実装計画
├── network-rag-system-integration-summary.md  # 連携要約
└── README.md                  # このファイル
```

## 🔧 構成要件

- Python 3.8+
- PyYAML>=6.0
- markdown>=3.4.3
- pathlib2>=2.3.7
- typing-extensions>=4.8.0

## 🤖 OpenHands連携

Network RAG SystemはOpenHandsと連携することで、LLM APIを活用した高度なネットワーク自動化を実現します。

### 主な機能

- **LLM API連携**: 内部LLM APIとのシームレスな連携
- **自動エージェント**: ネットワーク設定要求を自動処理
- **バッチ処理**: 複数設定の一括生成と検証
- **結果管理**: 生成された設定の保存とレポート作成
- **検証機能**: 設定構文とビジネスルールの検証

### セットアップ手順

1. **依存関係のインストール**
```bash
# 基本的な依存関係
pip install -r requirements/base.txt

# OpenHands連携用の追加依存関係
pip install openhands requests fastapi uvicorn
```

2. **設定ファイルの準備**
```python
# config.py
OPENHANDS_CONFIG = {
    'llm_api_url': 'http://your-llm-api:8000',
    'llm_api_key': 'your-api-key',
    'rag_system_path': '/path/to/network-rag-system',
    'enable_validation': True,
    'max_retries': 3,
    'timeout': 30
}
```

3. **エージェントの実行**
```python
from network_rag_system_integration_example import OpenHandsNetworkAgent, OpenHandsIntegrationConfig

# 設定の初期化
config = OpenHandsIntegrationConfig(
    llm_api_url="http://localhost:8000",
    llm_api_key="your-api-key",
    enable_validation=True
)

# エージェントの初期化
agent = OpenHandsNetworkAgent(config)

# 単一クエリの処理
result = agent.process_network_request(
    query="R1に新しい支社Cの接続を追加してOSPFで設定してください",
    device_name="R1",
    config_type="ospf"
)

# バッチ処理の実行
queries = [
    {"query": "R1に支社C接続を追加", "device_name": "R1", "config_type": "ospf"},
    {"query": "SW1にVLAN40を追加", "device_name": "SW1", "config_type": "interface"},
    {"query": "R2のセキュリティを強化", "device_name": "R2", "config_type": "security"}
]

results = agent.batch_process_requests(queries)

# 結果の保存
output_dir = agent.save_results(results)
print(f"結果を保存しました: {output_dir}")
```

### デプロイ構成

#### Docker Compose例
```yaml
version: '3.8'
services:
  openhands-agent:
    build: ./openhands
    ports:
      - "8001:8000"
    environment:
      - LLM_API_URL=http://llm-gateway:8000
      - RAG_API_URL=http://rag-system:8002
    volumes:
      - ./openhands:/app
      - ./network-rag-system:/rag-system
    depends_on:
      - llm-gateway
      - rag-system

  rag-system:
    build: ./network-rag-system
    ports:
      - "8002:8000"
    volumes:
      - ./network-rag-system:/app
      - ./knowledge-base:/app/knowledge-base

  llm-gateway:
    build: ./llm-gateway
    ports:
      - "8000:8000"
    environment:
      - LLM_MODEL=internal-model
      - LLM_API_KEY=your-api-key
```

### 使用例

#### 1. 基本的な設定生成
```python
# ルーターのOSPF設定生成
result = agent.process_network_request(
    query="R1に新しい支社Cの接続を追加してOSPFで設定してください",
    device_name="R1",
    config_type="ospf"
)

print(result['config_content'])
```

#### 2. スイッチのVLAN設定
```python
# スイッチのVLAN設定生成
result = agent.process_network_request(
    query="SW1にVLAN40を追加して開発部用に設定してください",
    device_name="SW1",
    config_type="interface"
)
```

#### 3. セキュリティ設定の強化
```python
# セキュリティポリシーの適用
result = agent.process_network_request(
    query="R2のセキュリティを強化してACLを追加してください",
    device_name="R2",
    config_type="security"
)
```

### 検証と品質保証

生成された設定は以下の検証を自動で実行します：

- **構文検証**: Cisco IOSコマンド構文のチェック
- **IPアドレス検証**: プライベートIPアドレス範囲の確認
- **OSPF検証**: エリア設定とネットワーク設定の検証
- **ACL検証**: ACL番号範囲の正当性チェック
- **デバイス固有検証**: デバイスタイプに応じた必須設定の確認

### トラブルシューティング

#### 常見の問題

1. **LLM API接続エラー**
   - APIサーバーの起動を確認
   - 認証情報の設定を確認
   - ネットワーク接続を確認

2. **RAGシステム読み込みエラー**
   - 知識ベースディレクトリの存在を確認
   - ファイルパーミッションを確認
   - YAMLファイルの構文を確認

3. **検証エラー**
   - 生成された設定の構文を手動で確認
   - 検証ルールの設定を確認
   - デバイスポリシーとの整合性を確認

#### ログの確認
```bash
# エージェントログの確認
tail -f /var/log/openhands-agent.log

# RAGシステムログの確認
tail -f /var/log/network-rag-system.log

# LLM APIログの確認
tail -f /var/log/llm-gateway.log
```

### パフォーマンス最適化

#### バッチ処理の最適化
```python
# 並列処理の有効化
import asyncio

async def parallel_processing(queries):
    tasks = [agent.process_network_request(q) for q in queries]
    return await asyncio.gather(*tasks)

# レートリミットの調整
config = OpenHandsIntegrationConfig(
    llm_api_url="http://localhost:8000",
    max_retries=3,
    timeout=10,  # タイムアウトの短縮
    enable_validation=True
)
```

### セキュリティ考慮事項

1. **APIキーの管理**
   - 環境変数またはシークレットマネージャーを使用
   - 定期的なキーのローテーション
   - アクセス権限の最小化

2. **ネットワークセキュリティ**
   - VPNを使用した内部APIへのアクセス
   - ファイアウォールルールの設定
   - 証明書ベースの認証

3. **データ保護**
   - 機密情報のマスキング
   - ログデータの暗号化
   - バックアップデータの保護

## 📖 ドキュメント

- [📖 ドキュメント](docs/README.md)
- [🔌 APIリファレンス](docs/API.md)
- [💡 使用例](docs/EXAMPLES.md)
- [🤝 貢献ガイド](docs/CONTRIBUTING.md)
- [🤖 OpenHands連携ガイド](network-rag-system-integration-plan.md)
- [📊 連携実装サマリー](network-rag-system-integration-summary.md)

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
