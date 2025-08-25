



# Network RAG System - Codebase Structure

## 主要モジュール

### src/rag_system.py (320行)
**NetworkRAGSystemクラス**
- クエリの解析と関連情報の検索
- デバイス、ポリシー、テンプレートの関連検索
- プロンプト生成機能
- クエリ履歴管理

**主要メソッド**
- `retrieve_relevant_info(query)`: 関連情報の検索
- `generate_config_prompt(query)`: プロンプト生成
- `_parse_query(query)`: クエリ解析
- `_find_relevant_devices(query)`: 関連デバイス検索
- `_find_relevant_policies(query)`: 関連ポリシー検索
- `_find_relevant_templates(query)`: 関連テンプレート検索

**QueryContextデータクラス**
- クエリのコンテキスト情報を保持
- device_name, requirements, config_type, priority

### src/config_generator.py (397行)
**NetworkConfigGeneratorクラス**
- コンフィグの自動生成
- テンプレート変数置換
- 検証機能
- 生成されたコンフィグの管理

**主要メソッド**
- `generate_config(query)`: コンフィグ生成
- `_generate_config_content(prompt)`: コンテンツ生成
- `_validate_config(config_content)`: 検証
- `_generate_metadata(query, config_content)`: メタデータ生成
- `save_config(config)`: コンフィグ保存

**GeneratedConfigデータクラス**
- 生成されたコンフィグ情報を保持
- device_name, config_type, config_content, validation_result, metadata

### src/knowledge_base.py (328行)
**KnowledgeBaseクラス**
- 知識ベースの一元管理
- デバイスポリシー、テンプレート、検証ルールの管理

**主要メソッド**
- `load_device_policies()`: デバイスポリシー読み込み
- `load_templates()`: テンプレート読み込み
- `load_validation_rules()`: 検証ルール読み込み
- `search_relevant_content(query)`: 関連コンテンツ検索

**DevicePolicyデータクラス**
- デバイスポリシー情報を保持
- device_name, device_type, configuration, policies

**Templateデータクラス**
- テンプレート情報を保持
- name, content, variables, description

### src/utils.py (285行)
**ユーティリティ関数群**
- IPアドレス検証
- コンフィグフォーマット
- バックアップ生成
- 変更履歴作成
- ネットワーク図作成
- ファイル操作

**主要関数**
- `validate_ip_address(ip)`: IPアドレス検証
- `validate_subnet_mask(mask)`: サブネットマスク検証
- `format_config_output(config)`: コンフィグフォーマット
- `generate_backup_filename()`: バックアップファイル名生成
- `generate_change_log(old_config, new_config)`: 変更履歴生成

### src/__init__.py (23行)
- パッケージの初期化
- バージョン情報の定義
- 主要クラスのインポート

## 知識ベース構造

### knowledge-base/devices/
- デバイスポリシー: R1_policy.md, R2_policy.md, SW1_policy.md
- デバイス設定: Cisco_IOS_XE_Router_Config.md, Cisco_IOS_XE_Switch_Config.md, etc.
- 実行コンフィグ: device_configs/ 配下

### knowledge-base/automation/
- テンプレート: templates/router-template.txt
- 検証ルール: validation-rules.yaml

## 使用例

### examples/basic_usage.py
- 基本的な使用方法のデモ
- 複数クエリのバッチ処理
- 生成結果の表示と保存

### run_kb_update.py
- 知識ベースの更新スクリプト
- 自動更新機能

### auto_kb_updater.py
- 自動知識ベース更新
- スケジュールされた更新

### network-rag-system-integration-example.py
- ネットワークRAGシステムの統合例
- OpenHands連携のデモ

## データフロー

1. **クエリ入力**: ユーザーが自然言語でクエリを入力
2. **情報検索**: RAGシステムが関連情報を検索
3. **プロンプト生成**: 検索結果からプロンプトを生成
4. **コンフィグ生成**: LLM APIでコンフィグを生成
5. **検証**: 生成されたコンフィグを検証
6. **出力**: 結果を表示または保存

## アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   ユーザー     │    │  Network RAG    │    │   Knowledge     │
│   インターフェース│    │   System        │    │   Base          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LLM API       │    │   Config        │    │   Validation    │
│   Gateway       │    │   Generator     │    │   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 拡張性
- モジュール設計により機能の追加が容易
- プラグイン方式での拡張が可能
- 外部LLM APIの切り替えが可能
- 知識ベースの動的更新が可能



