# Network RAG System

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Network RAG Systemは、Retrieval-Augmented Generation（RAG）技術を活用したネットワーク装置のコンフィグレーション自動生成システムです。**初心者でも簡単に使える**ように設計されており、事前に定義された知識ベース（KB）を活用して、一貫性のある高品質なネットワークコンフィグを自動生成します。

## 🎯 このシステムでできること

- **自然言語で設定生成**: 「R1の基本設定を生成して」のような簡単な言葉でコンフィグが生成できます
- **関連情報の自動検索**: クエリに基づいて関連するデバイス、ポリシー、テンプレートを自動的に検索
- **テンプレート変数置換**: `{{hostname}}` のような変数を自動的に置換して実際の設定を生成
- **検証機能**: 生成されたコンフィグの構文をチェックしてエラーを検出
- **日本語対応**: 日本語のクエリにも対応した日本語ネットワーク環境に最適化

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

### 3ステップで設定を生成！

#### ステップ1: システムの準備
```python
# 必要なモジュールをインポート
from src.rag_system import NetworkRAGSystem
from src.config_generator import NetworkConfigGenerator

# システムを初期化
rag_system = NetworkRAGSystem()
config_generator = NetworkConfigGenerator()
```

#### ステップ2: クエリを入力
```python
# 自然言語で設定要求を入力
query = "R1の基本設定を生成して"
```

#### ステップ3: 設定を生成
```python
# コンフィグを自動生成
generated_config = config_generator.generate_config(query)

# 結果を確認
print(f"デバイス: {generated_config.device_name}")
print(f"設定タイプ: {generated_config.config_type}")
print("生成されたコンフィグ:")
print(generated_config.config_content)
```

### 実行結果の例
```
=== Config for: R1の基本設定を生成して ===

! R1 - Router Configuration Template
! Generated based on network policy
! Requirements: R1の基本設定を生成して

! Basic Settings
hostname R1
ip routing
service timestamps debug datetime msec
service timestamps log datetime msec
no ip domain-lookup
ip domain-name company.local

! Interface Configuration
! GigabitEthernet0/0/0
! GigabitEthernet0/0/1

! OSPF Configuration
router ospf 1
 router-id 10.1.1.1
 passive-interface default
 no passive-interface {{active_interfaces}}

! Security Configuration


! High Availability


! Monitoring Configuration
```

### 複数設定の一括生成（バッチ処理）
```python
from src.config_generator import NetworkConfigGenerator

# コンフィグ生成器の初期化
config_generator = NetworkConfigGenerator()

# 複数の設定要求をリストで準備
batch_queries = [
    "R1の基本設定を生成して",
    "SW1の設定を教えて",
    "R2のOSPF設定を確認"
]

# 一括で設定を生成
for query in batch_queries:
    print(f"処理中: {query}")
    config = config_generator.generate_config(query)
    print(f"✓ {query}: {config.device_name} の設定を生成完了")
    print(f"  - 設定タイプ: {config.config_type}")
    print(f"  - 行数: {config.metadata['line_count']}")
    print("-" * 50)
```

### 実行結果の例
```
処理中: R1の基本設定を生成して
✓ R1の基本設定を生成して: R1 の設定を生成完了
  - 設定タイプ: general
  - 行数: 36
--------------------------------------------------
処理中: SW1の設定を教えて
✓ SW1の設定を教えて: SW1 の設定を生成完了
  - 設定タイプ: general
  - 行数: 35
--------------------------------------------------
処理中: R2のOSPF設定を確認
✓ R2のOSPF設定を確認: R2 の設定を生成完了
  - 設定タイプ: ospf
  - 行数: 36
--------------------------------------------------
```

## 🔍 システムの仕組み（初心者向け）

### Network RAG Systemはどうやって動くの？

Network RAG Systemは、以下の3つのステップで設定を自動生成します：

#### ステップ1: 情報の検索（Retrieval）
```
クエリ: "R1の基本設定を生成して"
↓
関連情報の検索
├── デバイス: R1（ルーター）
├── ポリシー: R1の設定ポリシー
└── テンプレート: router-template
```

#### ステップ2: 情報の統合（Augmentation）
```
検索した情報を統合
├── デバイスポリシーからホスト名: "R1"
├── デバイスタイプからテンプレート: "router-template"
└── テンプレート変数を準備
```

#### ステップ3: 設定の生成（Generation）
```
テンプレート + 変数 = 実際の設定
テンプレート: "{{hostname}} - Router Configuration"
↓
実際の設定: "R1 - Router Configuration"
```

### 主要なコンポーネント

#### 📚 知識ベース（Knowledge Base）
- **デバイスポリシー**: 各デバイスの設定要件
- **テンプレート**: 設定のひな形
- **ポリシー**: ネットワーク全体のルール

#### 🤖 RAGシステム（Retrieval-Augmented Generation）
- **関連情報検索**: クエリに合った情報を探す
- **テンプレートマッチング**: 適切なテンプレートを選択
- **変数置換**: テンプレートの変数を実際の値に置換

#### ⚙️ コンフィグ生成器（Config Generator）
- **設定生成**: テンプレートから実際の設定を生成
- **検証機能**: 生成された設定の構文をチェック
- **結果管理**: 生成結果を保存・管理

### 使い方の具体例

#### 例1: ルーターの基本設定
```python
# クエリ
query = "R1の基本設定を生成して"

# システムが内部で行う処理
1. "R1" というデバイスを検索
2. "ルーター" のテンプレートを選択
3. テンプレートの {{hostname}} を "R1" に置換
4. 実際の設定を生成
```

#### 例2: スイッチの設定
```python
# クエリ
query = "SW1の設定を教えて"

# システムが内部で行う処理
1. "SW1" というデバイスを検索
2. "L2/L3スイッチ" のテンプレートを選択
3. 必要な変数を置換
4. スイッチ用の設定を生成
```

### 🎯 このシステムのメリット

- **簡単な操作**: 複雑なネットワーク知識が不要
- **一貫性のある設定**: テンプレートにより設定の品質が安定
- **ミスの削減**: 手動設定による人的ミスを減らせる
- **効率化**: 短時間で大量の設定を生成可能
- **学習支援**: 生成された設定を学習材料として活用可能

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

## 🚀 デプロイガイド

### Ubuntuへのデプロイ手順

#### 1. 環境準備

##### 1.1 システムの更新
```bash
# システムの更新
sudo apt update && sudo apt upgrade -y

# 基本的なツールのインストール
sudo apt install -y curl wget git vim unzip htop

# Pythonとpipのインストール
sudo apt install -y python3 python3-pip python3-venv

# Pythonパッケージのアップグレード
pip3 install --upgrade pip
```

##### 1.2 仮想環境の作成
```bash
# プロジェクトディレクトリの作成
sudo mkdir -p /opt/network-rag-system
sudo chown -R $USER:$USER /opt/network-rag-system
cd /opt/network-rag-system

# リポジトリのクローン
git clone https://github.com/kaishin0527/network-rag-system.git .

# 仮想環境の作成
python3 -m venv venv
source venv/bin/activate

# 仮想環境を有効化するためのスクリプト作成
echo 'source /opt/network-rag-system/venv/bin/activate' | sudo tee /etc/profile.d/network-rag-env.sh
sudo chmod +x /etc/profile.d/network-rag-env.sh
```

#### 2. 依存関係のインストール

##### 2.1 基本的な依存関係
```bash
# Network RAG Systemの依存関係
pip install -r requirements/base.txt

# OpenHands関連の依存関係
pip install openhands requests fastapi uvicorn paramiko

# 追加の依存関係
pip install pyyaml markdown pathlib2 typing-extensions
```

##### 2.2 ディレクトリ構造の作成
```bash
# 必要なディレクトリの作成
sudo mkdir -p /var/log/network-rag-system
sudo mkdir -p /etc/network-rag-system
sudo mkdir -p /var/lib/network-rag-system/backups
sudo mkdir -p /var/lib/network-rag-system/temp

# パーミッションの設定
sudo chown -R $USER:$USER /var/log/network-rag-system
sudo chown -R $USER:$USER /etc/network-rag-system
sudo chown -R $USER:$USER /var/lib/network-rag-system
```

#### 3. 設定ファイルの作成

##### 3.1 Network RAG System設定
```bash
# 基本的な設定ファイルを作成
sudo tee /etc/network-rag-system/config.yml > /dev/null << 'EOF'
# Network RAG System Configuration
version: 1.0.0

# Database Settings
database:
  type: sqlite
  path: /var/lib/network-rag-system/network_rag.db

# Logging Settings
logging:
  level: INFO
  file: /var/log/network-rag-system/app.log
  max_size: 10MB
  backup_count: 5

# API Settings
api:
  host: 0.0.0.0
  port: 8000
  debug: false

# OpenHands Integration
openhands:
  enabled: true
  api_url: http://localhost:8001
  api_key: your-api-key-here
  timeout: 30
  max_retries: 3

# Auto Update Settings
auto_update:
  enabled: true
  interval: 3600  # 1 hour
  batch_size: 5
  max_retries: 3
  timeout: 300

# SSH Settings for device access
ssh:
  default_timeout: 30
  default_port: 22
  key_file: /etc/network-rag-system/ssh_key
  known_hosts: /etc/network-rag-system/known_hosts

# Security
security:
  enable_auth: true
  secret_key: your-secret-key-here
  jwt_expiry: 24h
EOF
```

##### 3.2 OpenHands設定
```bash
# OpenHands設定ディレクトリの作成
mkdir -p ~/.openhands

# OpenHands設定ファイルを作成
tee ~/.openhands/config.yml > /dev/null << 'EOF'
# OpenHands Configuration
version: 1.0.0

# Agent Settings
agent:
  name: network-rag-agent
  type: network
  max_iterations: 100
  timeout: 300

# LLM Integration
llm:
  provider: openai
  model: gpt-4
  api_key: your-llm-api-key
  base_url: http://localhost:8000

# Network Settings
network:
  rag_system_path: /opt/network-rag-system
  knowledge_base_path: /opt/network-rag-system/knowledge-base
  temp_dir: /var/lib/network-rag-system/temp

# Logging
logging:
  level: INFO
  file: /var/log/network-rag-system/openhands.log
EOF
```

#### 4. サービスの作成

##### 4.1 サービススクリプトの作成
```bash
# Network RAG Systemサービススクリプト
tee /opt/network-rag-system/start_service.sh > /dev/null << 'EOF'
#!/bin/bash
# Network RAG System Service Startup Script

cd /opt/network-rag-system
source venv/bin/activate

# Network RAG System APIサーバーを起動
nohup python -m fastapi src.api:app --host 0.0.0.0 --port 8000 > /var/log/network-rag-system/rag_api.log 2>&1 &
RAG_API_PID=$!

# KBアップdaterサービスを起動
nohup python auto_kb_updater.py > /var/log/network-rag-system/kb_updater.log 2>&1 &
KB_UPDATER_PID=$!

echo $RAG_API_PID > /var/run/network-rag-api.pid
echo $KB_UPDATER_PID > /var/run/network-rag-updater.pid

echo "Network RAG System services started"
echo "RAG API PID: $RAG_API_PID"
echo "KB Updater PID: $KB_UPDATER_PID"
EOF

chmod +x /opt/network-rag-system/start_service.sh

# OpenHandsサービススクリプト
sudo mkdir -p /opt/openhands
sudo chown -R $USER:$USER /opt/openhands

tee /opt/openhands/start_service.sh > /dev/null << 'EOF'
#!/bin/bash
# OpenHands Service Startup Script

cd /opt/openhands
source /opt/network-rag-system/venv/bin/activate

# OpenHandsサービスをバックグラウンドで実行
nohup python -m openhands.server --config ~/.openhands/config.yml > /var/log/network-rag-system/openhands.log 2>&1 &
OPENHANDS_PID=$!

echo $OPENHANDS_PID > /var/run/openhands.pid

echo "OpenHands service started with PID: $OPENHANDS_PID"
EOF

chmod +x /opt/openhands/start_service.sh
```

##### 4.2 systemdサービスの作成
```bash
# Network RAG Systemサービス用のsystemdファイル
sudo tee /etc/systemd/system/network-rag-system.service > /dev/null << 'EOF'
[Unit]
Description=Network RAG System
After=network.target
Wants=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/opt/network-rag-system
ExecStart=/opt/network-rag-system/start_service.sh
ExecStop=/bin/kill -TERM $(cat /var/run/network-rag-api.pid) $(cat /var/run/network-rag-updater.pid)
ExecReload=/bin/kill -HUP $(cat /var/run/network-rag-api.pid) $(cat /var/run/network-rag-updater.pid)
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# OpenHandsサービス用のsystemdファイル
sudo tee /etc/systemd/system/openhands.service > /dev/null << 'EOF'
[Unit]
Description=OpenHands Service
After=network.target network-rag-system.service
Wants=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/opt/openhands
ExecStart=/opt/openhands/start_service.sh
ExecStop=/bin/kill -TERM $(cat /var/run/openhands.pid)
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

#### 5. ファイアウォール設定

```bash
# ファイアウォールの設定
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 8000/tcp  # Network RAG API
sudo ufw allow 8001/tcp  # OpenHands API
sudo ufw allow 8080/tcp  # Web UI (if needed)

# ファイアウォールの有効化
sudo ufw --force enable
```

#### 6. サービスの起動

##### 6.1 サービスの有効化と起動
```bash
# systemdサービスのリロード
sudo systemctl daemon-reload

# Network RAG Systemサービスの有効化と起動
sudo systemctl enable network-rag-system
sudo systemctl start network-rag-system

# OpenHandsサービスの有効化と起動
sudo systemctl enable openhands
sudo systemctl start openhands

# サービスの状態確認
sudo systemctl status network-rag-system
sudo systemctl status openhands
```

##### 6.2 動作確認
```bash
# Network RAG System APIの確認
curl -X GET "http://localhost:8000/health" -H "accept: application/json"

# OpenHands APIの確認
curl -X GET "http://localhost:8001/health" -H "accept: application/json"

# KB更新機能のテスト
cat > /tmp/test_config.json << 'EOF'
{
  "device_name": "TEST-R1",
  "config_type": "running_config",
  "config_content": "! Test Configuration\nhostname TEST-R1\nip routing\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n no shutdown\nend",
  "metadata": {
    "source": "test",
    "backup_date": "2025-01-10",
    "admin": "test-admin"
  }
}
EOF

python run_kb_update.py --mode manual --input /tmp/test_config.json --report
```

#### 7. 便利なスクリプトの作成

##### 7.1 デプロイスクリプト
```bash
# デプロイスクリプト
sudo mkdir -p /opt/network-rag-system/deploy
sudo chown -R $USER:$USER /opt/network-rag-system/deploy

tee /opt/network-rag-system/deploy/deploy.sh > /dev/null << 'EOF'
#!/bin/bash
# Complete Deployment Script

echo "Starting Network RAG System deployment..."

# 仮想環境の有効化
source /opt/network-rag-system/venv/bin/activate
cd /opt/network-rag-system

# サービスの起動
sudo systemctl start network-rag-system
sudo systemctl start openhands

# サービスの状態確認
echo "Checking service status..."
sudo systemctl status network-rag-system --no-pager -l
sudo systemctl status openhands --no-pager -l

# APIの動作確認
echo "Checking API connectivity..."
curl -s http://localhost:8000/health > /dev/null && echo "✓ Network RAG API is running" || echo "✗ Network RAG API is not running"
curl -s http://localhost:8001/health > /dev/null && echo "✓ OpenHands API is running" || echo "✗ OpenHands API is not running"

echo "Deployment completed!"
EOF

chmod +x /opt/network-rag-system/deploy/deploy.sh

# 停止スクリプト
tee /opt/network-rag-system/deploy/stop.sh > /dev/null << 'EOF'
#!/bin/bash
# Stop Services Script

echo "Stopping Network RAG System services..."

sudo systemctl stop network-rag-system
sudo systemctl stop openhands

echo "All services stopped."
EOF

chmod +x /opt/network-rag-system/deploy/stop.sh

# バックアップスクリプト
tee /opt/network-rag-system/deploy/backup.sh > /dev/null << 'EOF'
#!/bin/bash
# Backup Script

BACKUP_DIR="/var/lib/network-rag-system/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="network_rag_backup_$DATE.tar.gz"

echo "Creating backup: $BACKUP_FILE"

# バックアップの作成
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
  --exclude="*.log" \
  --exclude="temp/*" \
  --exclude="backups/*" \
  /opt/network-rag-system \
  /etc/network-rag-system \
  /var/lib/network-rag-system

# 古いバックアップの削除（30日以上前）
find "$BACKUP_DIR" -name "network_rag_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/$BACKUP_FILE"
EOF

chmod +x /opt/network-rag-system/deploy/backup.sh
```

##### 7.2 定期バックアップの設定
```bash
# 定期バックアップの設定
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/network-rag-system/deploy/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "0 3 * * * sudo systemctl restart network-rag-system") | crontab -
```

#### 8. 最終確認

##### 8.1 システムの状態確認
```bash
# 全サービスの状態確認
sudo systemctl list-units --type=service --state=running | grep -E "(network-rag|openhands)"

# リソース使用状況の確認
htop

# ディスク使用状況の確認
df -h
```

##### 8.2 アクセス方法
```bash
# APIアクセス方法
echo "Network RAG System API: http://$(hostname -I | awk '{print $1}'):8000"
echo "OpenHands API: http://$(hostname -I | awk '{print $1}'):8001"

# サービス管理方法
echo "Service management:"
echo "  sudo systemctl start network-rag-system"
echo "  sudo systemctl stop network-rag-system"
echo "  sudo systemctl restart network-rag-system"
echo "  sudo systemctl status network-rag-system"
```

### サービス管理コマンド

#### サービスの起動・停止・再起動
```bash
# サービスの起動
sudo systemctl start network-rag-system
sudo systemctl start openhands

# サービスの停止
sudo systemctl stop network-rag-system
sudo systemctl stop openhands

# サービスの再起動
sudo systemctl restart network-rag-system
sudo systemctl restart openhands

# サービスの状態確認
sudo systemctl status network-rag-system
sudo systemctl status openhands

# サービスの有効化・無効化
sudo systemctl enable network-rag-system    # 起動時に自動起動
sudo systemctl disable network-rag-system   # 起動時に自動起動しない
```

#### ログの確認
```bash
# systemdサービスログの確認
sudo journalctl -u network-rag-system -f
sudo journalctl -u openhands -f

# アプリケーションログの確認
tail -f /var/log/network-rag-system/app.log
tail -f /var/log/network-rag-system/openhands.log
tail -f /var/log/network-rag-system/rag_api.log
tail -f /var/log/network-rag-system/kb_updater.log
```

#### バックアップと復元
```bash
# バックアップの作成
sudo /opt/network-rag-system/deploy/backup.sh

# バックアップの一覧
ls -la /var/lib/network-rag-system/backups/

# バックアップからの復元
sudo systemctl stop network-rag-system
sudo tar -xzf /var/lib/network-rag-system/backups/network_rag_backup_YYYYMMDD_HHMMSS.tar.gz -C /
sudo systemctl start network-rag-system
```

### トラブルシューティング

#### サービス起動時の問題
```bash
# サービスの詳細なログ確認
sudo journalctl -u network-rag-system --no-pager -n 50
sudo journalctl -u openhands --no-pager -n 50

# 依存関係の確認
sudo systemctl list-dependencies network-rag-system
sudo systemctl list-dependencies openhands

# ポートの競合確認
sudo netstat -tulpn | grep -E ":800[01]"
```

#### パーミッションの問題
```bash
# パーミッションの確認と修正
sudo chown -R $USER:$USER /opt/network-rag-system
sudo chown -R $USER:$USER /var/log/network-rag-system
sudo chown -R $USER:$USER /etc/network-rag-system
sudo chown -R $USER:$USER /var/lib/network-rag-system

# 実行権限の確認
ls -la /opt/network-rag-system/start_service.sh
ls -la /opt/openhands/start_service.sh
```

#### ネットワーク接続の問題
```bash
# ファイアウォールの状態確認
sudo ufw status

# ポートの開放
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp

# ネットワーク接続の確認
curl -v http://localhost:8000/health
curl -v http://localhost:8001/health
```

### カスタマイズ

#### 設定ファイルの編集
```bash
# Network RAG System設定の編集
sudo nano /etc/network-rag-system/config.yml

# OpenHands設定の編集
nano ~/.openhands/config.yml

# ログレベルの変更
# logging:
#   level: DEBUG  # 開発時はDEBUGに変更
```

#### 自動更新設定の変更
```bash
# 自動更新間隔の変更（1時間 → 30分）
sudo sed -i 's/interval: 3600/interval: 1800/' /etc/network-rag-system/config.yml

# バッチサイズの変更
sudo sed -i 's/batch_size: 5/batch_size: 10/' /etc/network-rag-system/config.yml
```

### まとめ

このデプロイガイドにより、以下の環境が構築されます：

- ✅ **Network RAG System**: APIサーバーとKB更新機能
- ✅ **OpenHands**: LLMエージェントとの連携機能
- ✅ **自動更新**: 定期的なKB更新機能
- ✅ **バックアップ**: 自動バックアップ機能
- ✅ **監視**: サービス監視とログ管理
- ✅ **セキュリティ**: ファイアウォールとアクセス制御

デプロイが完了したら、以下のURLでサービスにアクセスできます：

- **Network RAG System API**: `http://サーバーのIPアドレス:8000`
- **OpenHands API**: `http://サーバーのIPアドレス:8001`

KB更新機能を使用するには、`python run_kb_update.py` コマンドを使用してください。

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
