



# Network RAG System - Task Completion Guidelines

## タスク完了時のチェックリスト

### 1. コード品質チェック
- [ ] Blackによるコードフォーマットを実行
- [ ] isortによるインポートソートを実行
- [ ] flake8によるリンティングを実行
- [ ] mypyによる型チェックを実行
- [ ] 全てのチェックにパスしていること

### 2. テスト実行
- [ ] pytestによるテストを実行
- [ ] テストカバレッジが80%以上であること
- [ ] 新しい機能のテストを追加
- [ ] 統合テストを実行

### 3. ドキュメント更新
- [ ] README.mdを更新
- [ ] 関連するドキュメントを更新
- [ ] 使用例を追加または更新
- [ ] CHANGELOG.mdに変更を記載

### 4. 機能テスト
- [ ] 基本的な使用例を実行
- [ ] バッチ処理をテスト
- [ ] 知識ベース更新をテスト
- [ ] エラーハンドリングをテスト

### 5. パフォーマンスチェック
- [ ] 実行時間を測定
- [ ] メモリ使用量を確認
- [ ] 大規模データ処理をテスト

### 6. セキュリティチェック
- [ ] 入力値の検証
- [ ] エスケープ処理
- [ ] 権限チェック

### 7. 互換性チェック
- [ ] Python 3.8+で動作確認
- [ ] 主要OSで動作確認
- [ ] 依存関係のバージョン互換性

### 8. デプロイ準備
- [ ] パッケージビルド
- [ ] インストール手順の確認
- [ ] 環境変数の設定

## タスク完了時のコマンド

### 品質チェック
```bash
# コードフォーマット
black src/ examples/

# インポートソート
isort src/ examples/

# リンティング
flake8 src/ examples/

# 型チェック
mypy src/
```

### テスト実行
```bash
# テスト実行
pytest tests/ -v

# カバレッジ確認
pytest --cov=src --cov-report=term-missing

# 統合テスト
python examples/basic_usage.py
python network-rag-system-integration-example.py
```

### ドキュメント更新
```bash
# ドキュメント確認
cat README.md
cat CHANGELOG.md

# 使用例実行
python examples/basic_usage.py
```

### 最終確認
```bash
# 全体の動作確認
python -c "
from src.rag_system import NetworkRAGSystem
from src.config_generator import NetworkConfigGenerator

rag_system = NetworkRAGSystem()
config_generator = NetworkConfigGenerator()

# 基本的なテスト
query = 'R1の基本設定を生成して'
config = config_generator.generate_config(query)
print(f'Generated config for: {config.device_name}')
print(f'Config type: {config.config_type}')
print(f'Validation: {config.validation_result}')
"
```

## 提出物
- [ ] ソースコード
- [ ] テストコード
- [ ] ドキュメント
- [ ] 使用例
- [ ] 変更履歴

## 注意事項
- 全てのコマンドはリポジトリのルートディレクトリで実行
- 仮想環境を使用することを推奨
- 変更前には必ずバックアップを取る
- タスク完了前に必ず全てのチェックを実行

## トラブルシューティング
- テストが失敗した場合は、依存関係を再インストール
- 型チェックでエラーが出た場合は、型ヒントを修正
- リンティングでエラーが出た場合は、コードスタイルを修正
- パフォーマンス問題がある場合は、プロファイリングを実施



