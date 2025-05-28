# expired-file-remover 開発ガイド

このドキュメントでは、`expired-file-remover` パッケージの開発に参加するための情報を提供します。

## 開発環境のセットアップ

### Dev Container を使用する場合

このプロジェクトは Dev Container を使用して開発環境を簡単に構築できます。

1. [Visual Studio Code](https://code.visualstudio.com/) と [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) 拡張機能をインストール
2. リポジトリをクローン
3. VS Code でフォルダを開く
4. VS Code の左下の緑色のボタンをクリックし、「Reopen in Container」を選択
5. Dev Container のビルドが完了すると、すべての依存関係がインストールされた環境が準備されます

### 手動セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/your-username/expired-file-remover.git
cd expired-file-remover

# Poetry をインストール（未インストールの場合）
curl -sSL https://install.python-poetry.org | python3 -

# 依存関係をインストール
poetry install
```

## 開発ワークフロー

### テストの実行

```bash
# すべてのテストを実行
poetry run pytest

# カバレッジレポートを出力
poetry run pytest --cov=src/expired_file_remover
```

### コードスタイル

このプロジェクトでは、以下のツールを使用してコードのフォーマットと品質を確保しています：

- **isort**: インポート文の整理
- **black**: コードフォーマットの統一
- **flake8**: スタイルガイドに基づくリンティング
- **mypy**: 静的型チェック

```bash
# コードフォーマットの適用
poetry run isort .
poetry run black .

# リンティングと型チェックの実行
poetry run flake8
poetry run mypy src/expired_file_remover tests
```

### CI/CD パイプライン

プロジェクトには GitHub Actions ワークフローが設定されており、プッシュとプルリクエスト時に自動的に以下を実行します：

1. コードのフォーマットチェック（flake8, isort）
2. 型チェック（mypy）
3. テストの実行（pytest）

## リリースプロセス

新しいバージョンをリリースするには：

1. バージョン番号を `pyproject.toml` で更新
2. CHANGELOG.md を更新
3. タグを作成: `git tag vX.Y.Z`
4. タグをプッシュ: `git push --tags`

GitHub Actions ワークフローがタグをトリガーとして PyPI にパッケージを公開します。

## プロジェクト構造

```
expired-file-remover/
├── .github/               # GitHub Actions ワークフロー
├── src/
│   └── expired_file_remover/  # メインパッケージ
│       ├── __init__.py    # パッケージエクスポート
│       └── core.py        # コア機能
├── tests/                 # テストケース
│   └── test_basic.py      # 基本機能のテスト
├── pyproject.toml         # パッケージメタデータと設定
├── LICENSE                # ライセンスファイル
└── README.md              # ユーザー向けドキュメント
```

## 貢献ガイドライン

1. フォークして機能ブランチを作成
2. 変更を加える
3. テストを追加/更新
4. コードフォーマットとリントを適用
5. プルリクエストを作成

すべてのコントリビューションにはテストが必要です。