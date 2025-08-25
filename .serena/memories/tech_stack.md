

# Network RAG System Tech Stack

## 主要技術
- **プログラミング言語**: Python 3.8+
- **RAGフレームワーク**: カスタム実装（外部LLM API連携対応）
- **データフォーマット**: YAML, Markdown
- **パッケージ管理**: pip, setuptools

## 依存関係
### 基本依存関係 (base.txt)
- PyYAML>=6.0 - YAMLファイルの処理
- markdown>=3.4.3 - Markdownファイルの処理
- pathlib2>=2.3.7 - パス操作
- typing-extensions>=4.8.0 - 型ヒント

### 開発依存関係 (dev.txt)
- black>=22.0.0 - コードフォーマッタ
- flake8>=5.0.0 - リンター
- isort>=5.10.0 - インポートソート
- mypy>=1.0.0 - 静的型チェック
- pre-commit>=2.20.0 - コミット前チェック
- pytest>=7.0.0 - テストフレームワーク
- pytest-cov>=4.0.0 - カバレッジ
- pytest-mock>=3.10.0 - モック

### テスト依存関係 (test.txt)
- pytest>=7.0.0
- pytest-cov>=4.0.0
- pytest-mock>=3.10.0
- coverage>=6.0.0

## ビルドツール
- setuptools>=45
- wheel
- setuptools_scm[toml]>=6.2

## コンテナ化
- Docker/Docker Compose対応（計画中）

## 外部連携
- OpenHandsエージェント連携
- LLM API連携（社内LLM対応）
- CI/CDツール連携（digdag対応）

