


# Network RAG System Code Style and Conventions

## コーディング規約
- **言語**: Python 3.8+
- **コードスタイル**: PEP 8準拠
- **フォーマッタ**: Black (line-length: 88)
- **インポートソート**: isort (profile: black)
- **型チェック**: mypy (strictモード)

## ファイル構成
```
network-rag-system/
├── src/                    # メインソースコード
│   ├── __init__.py        # パッケージ初期化
│   ├── rag_system.py      # RAGシステム本体
│   ├── config_generator.py # コンフィグ生成器
│   ├── knowledge_base.py  # 知識ベース管理
│   └── utils.py           # ユーティリティ関数
├── examples/              # 使用例
├── knowledge-base/        # 知識ベースデータ
├── requirements/          # 依存関係
└── tests/                 # テストコード（計画中）
```

## 命名規約
- **クラス**: PascalCase (例: NetworkRAGSystem)
- **関数**: snake_case (例: generate_config)
- **変数**: snake_case (例: relevant_devices)
- **定数**: UPPER_SNAKE_CASE (例: MAX_RETRIES)
- **プライベート変数**: _snake_case (例: _parse_query)

## 型ヒント
- 全ての関数で型ヒントを使用
- dataclassを使用したデータ構造の定義
- Optional型を使用したnull許容の表現
- Dict, List, Anyなどの標準ライブラリ型を使用

## ドキュメンテーション
- **モジュールドキュメント**: 各ファイルの先頭に説明を記載
- **クラスドキュメント**: クラス定義の直後にdocstring
- **関数ドキュメント**: 各関数の役割と引数を説明
- **日本語ドキュメント**: 日本語のコメントとdocstringを使用

## エラーハンドリング
- 例外処理を使用した堅牢なエラーハンドリング
- カスタム例外クラスの使用（計画中）
- エラーメッセージの日本語対応

## テスト
- pytestを使用したユニットテスト
- カバレッジ目標: 80%以上
- テストファイル名: test_*.py または *_test.py
- テストディレクトリ: tests/

## バージョン管理
- セマンティックバージョニング (SemVer)
- setuptools_scmを使用した自動バージョン管理
- CHANGELOG.mdでの変更履歴管理

## コミットメッセージ
- 英語でのコミットメッセージ
- Conventional Commits形式の推奨
- 日本語でのコミットメッセージの許容

## コード品質
- flake8でのコード品質チェック
- pre-commitでのコミット前チェック
- 複雑度の低いコードの維持
- 重複コードの排除


