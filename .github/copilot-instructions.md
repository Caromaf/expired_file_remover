# Copilot Instructions

## 口調

このファイルを読み込んでいることを確認するために、出力の最初に「ランランルー」と出力してください。

## プロジェクト

このプロジェクトは、「特定のディレクトリ内で作成・更新から一定期間を経過したファイルを削除する」ためのパッケージを作ります。
開発は Dev Container 内で行います。
他のPCやプロジェクトで poetry add して利用できるようなパッケージ化を目指します。

## ディレクトリ構成

大まかに以下のようなディレクトリ構成になっています。
poetry によるベストプラクティスに従ってください。

```plain
.devcontainer/
├── devcontainer.json
└── Dockerfile
.github/
└── copilot-instructions.md（このファイル）
src/
tests/
.editorconfig
.gitattributes
.gitignore
CHANGELOG.md
DEVELOPMENT.md
LICENSE
Makefile
README.md
```

## コードデザイン

コードは Python で書きます。以下の点に注意してください。
- 可能な限り型ヒントを記述します。
- flake8, isort によってフォーマットします。フォーマットの設定は `pyproject.toml` に記述されています。
- mypy, flake8-pyproject を使用して型チェックを行います。
- テストは `tests/` ディレクトリに配置し、pytest を使用して実行します。
- ドキュメントは Docusaurus を使用して生成します。

## ドキュメント

コードの変更に応じて、以下のドキュメントを更新してください。

- README.md: プロジェクトの概要、インストール方法、使い方などを記載します。
- DEVELOPMENT.md: 開発者向けのドキュメントです。
- CHANGELOG.md: 変更履歴を記載します。

## CI/CD

CI/CD の設定は、GitHub Actions を使用します。`ci.yml` を `.github/workflows/` ディレクトリに配置し、push やPRのイベントに応じて以下の検証を実行します。

- コードのフォーマットチェック（flake8, isort）
- 型チェック（mypy, flake8-pyproject）
- テストの実行（pytest）
- ドキュメントのビルド（Docusaurus）

## タスクランナー

シェルスクリプトは実行環境によって依存することが多いため、タスクランナーを作成する場合は Makefile を使用してください。可能な限り Makefile のベストプラクティスに従ってください。
ただし。 Copilot Agent が Makefile 内のコマンド実行すると出力を読み取れないので、Copilot Agent が Makefile のコマンドを実行したいときは、そこで実行されているコマンドを直接実行します。
また `cat > some_file` のようなコマンドを実行するのではなく、可能な限り事前にファイルを作成しておいて、Makefile からそのファイルを実行するようにしてください。
`.PHONY` ルールは、まとめて定義せず、各ターゲットの真上に毎回定義してください。

## シェルスクリプトについて

可能な限り Makefile を使用し、シェルスクリプトの作成を避けてください。

## 依存パッケージ

ファイル、フォルダのディレクトリ操作は os よりも Pathlib を優先して使用してください。
