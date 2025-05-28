# Dev Containers を使って Python 開発環境を構築する方法

Dev Containers を使うと、Docker コンテナ内で Python 開発環境を簡単にセットアップできます。
poetry と Python が用意された Dev Container を使います。
Dev Container 自体のセットアップ方法は [dev_containers.md](dev_containers.md) を参照してください。

## 元々あると良いファイル

```plain
.devcontainer/
├── devcontainer.json
└── Dockerfile
.github/
└── copilot-instructions.md
src/
.editorconfig
.gitattributes
.gitignore
CHANGELOG.md
DEVELOPMENT.md
LICENSE
Makefile
README.md
```

## poetry プロジェクトを作成する

### pyproject.toml を作成する

Dev Container 内でターミナルを開きます。

```bash
# プロジェクトのルートディレクトリに移動します。
cd /workspaces/my_project

# poetry プロジェクトを初期化します。
poetry init
```

### すでにあるプロジェクトを使う場合

すでに `pyproject.toml` がある場合は、以下のコマンドで依存関係をインストールします。

```bash
# プロジェクトのルートディレクトリに移動します。
cd /workspaces/my_project
# 依存関係をインストールします。
poetry install
```

## src レイアウトの使用

プロジェクトのソースコードを `src` ディレクトリに配置するレイアウトは、Python プロジェクトで推奨される構成です。

### ディレクトリ構造

```plain
プロジェクト/
├── pyproject.toml
├── src/
│   └── パッケージ名/
│       ├── __init__.py
│       └── core.py
└── tests/
    ├── __init__.py
    └── test_basic.py
```

### pyproject.toml の設定

src レイアウトを使用する場合、`pyproject.toml` に以下のように `packages` を設定します：

```toml
[project]
name = "プロジェクト名"
version = "0.1.0"

[tool.poetry]
packages = [{include = "パッケージ名", from = "src"}]

[tool.poetry.dependencies]
python = "^3.11"
# その他の依存関係
```

この設定によって、Poetry は `src` ディレクトリ内のパッケージを正しく認識できるようになります。
