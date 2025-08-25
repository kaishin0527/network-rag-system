


# Network RAG System - Suggested Commands

## 環境セットアップ
```bash
# リポジトリのクローン
git clone https://github.com/kaishin0527/network-rag-system.git
cd network-rag-system

# 仮想環境の作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows

# 依存関係のインストール
pip install -r requirements/base.txt      # 基本依存関係
pip install -r requirements/dev.txt       # 開発依存関係
pip install -r requirements/test.txt      # テスト依存関係

# 開発環境のセットアップ
pre-commit install
```

## 開発コマンド
```bash
# コードフォーマット
black src/ examples/

# インポートソート
isort src/ examples/

# リンティング
flake8 src/ examples/

# 型チェック
mypy src/

# テスト実行
pytest tests/ -v

# カバレッジ確認
pytest --cov=src --cov-report=html

# テストとカバレッジ
pytest tests/ --cov=src --cov-report=term-missing
```

## 実行コマンド
```bash
# 基本的な使用例
python examples/basic_usage.py

# 知識ベース更新
python run_kb_update.py

# 自動知識ベース更新
python auto_kb_updater.py

# OpenHands統合例
python openhands_kb_updater_example.py

# ネットワークRAGシステム統合例
python network-rag-system-integration-example.py
```

## ビルドとデプロイ
```bash
# パッケージビルド
python -m build

# パッケージインストール（開発用）
pip install -e .

# Dockerビルド（計画中）
docker build -t network-rag-system .

# Docker Compose起動（計画中）
docker-compose up -d
```

## Git操作
```bash
# ブランチ一覧
git branch -a

# コミット履歴
git log --oneline -10

# ステータス確認
git status

# 差分確認
git diff

# スタッシュ
git stash
git stash pop
```

## デバッグ
```bash
# Pythonデバッグ
python -m pdb examples/basic_usage.py

# ログレベル設定
export PYTHONPATH=/workspace/network-rag-system:$PYTHONPATH
python examples/basic_usage.py

# 依存関係確認
pip list
pip freeze
```

## ドキュメント生成
```bash
# READMEの確認
cat README.md

# 知識ベースの確認
cat knowledge-base/README.md

# 統合計画の確認
cat network-rag-system-integration-plan.md

# 統合サマリーの確認
cat network-rag-system-integration-summary.md
```

## その他
```bash
# ファイル検索
find . -name "*.py" -type f
find . -name "*.md" -type f

# コード行数確認
wc -l src/*.py

# ディスク使用量確認
du -sh *
```

## 注意事項
- 全てのコマンドはリポジトリのルートディレクトリで実行
- Python 3.8+ の環境が必要
- 仮想環境の使用を推奨
- 開発時はpre-commitを有効化することを推奨


