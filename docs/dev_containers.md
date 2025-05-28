# Dev Containers

開発するプロダクトを Docker コンテナに閉じ込めるのではなく、さらに開発する環境そのものを Docker コンテナに閉じ込める機能です。

例えば Python と Django で Web アプリケーションを開発している場合：
- `.devcontainer/`: Pythonのバージョン、Djangoの関連ツール、Gitなどがインストールされた開発環境コンテナを定義します。
- アプリケーション側の Dockerfileなど: 開発したDjangoアプリケーションを本番環境で動かすために必要なPythonのランタイム、依存ライブラリ、アプリケーションコードなどをコンテナに含めます。

## 必要なもの

- Docker
- Docker Desktop（WindowsやMacでDockerを使う場合）
- Visual Studio Code（または Cursor など Dev Containers をサポートするエディタ）
- Dev Containers 拡張機能

## Dev Containers を構成するファイル

Dev Containers に関するファイルはプロジェクトルートの `.devcontainer/` ディレクトリ以下に配置します。

### `devcontainer.json`

Dev Containerの挙動を定義する最も重要なファイルです。

**メジャーな設定項目**

- `name`: コンテナの名前
- `image`: ベースとなるDockerイメージを指定します（例: mcr.microsoft.com/devcontainers/base:ubuntu）。
- `build`: Dockerfileを使って独自のイメージをビルドする場合に設定します。
    - `dockerfile`: Dockerfileのパスを指定します（例: `"dockerfile": "Dockerfile"`）。
    - `context`: ビルドコンテキストのパスを指定します（通常は..でプロジェクトルート）。
- `dockerComposeFile`: compose.ymlを使用する場合にパスを指定します（例: `"dockerComposeFile": ["../compose.yml"]`）。
- `service`: compose.ymlで複数のサービスを定義している場合、VS Codeが接続するサービスを指定します。
- `workspaceFolder`: コンテナ内のワークスペースディレクトリのパス（通常は/workspaces/your-projectなど）。
- `settings`: VS Codeのエディタ設定をコンテナ内で適用します（例: terminal.integrated.shell.linux）。
- `extensions`: コンテナ起動時に自動でインストールされるVS Code拡張機能のIDを配列で指定します。
- `postCreateCommand`: コンテナ作成後に一度だけ実行されるコマンド。依存関係のインストール（npm install、pip installなど）によく使われます。
- `postStartCommand`: コンテナ起動時に毎回実行されるコマンド。
- `forwardPorts`: ホストマシンにフォワードするポート番号を指定します（例: [3000, 8000]）。ウェブアプリケーションの開発などで使われます。
- `remoteUser`: コンテナ内で使用するユーザー。デフォルトはvscodeですが、rootなどに変更することも可能です。

## Dev Containers のはじめ方

### `devcontainer.json` がない場合

- cmd + shift + p でコマンドパレットを開きます
- Dev Containers: Reopen in Container を選択します
- 「ワークスペースに構成を追加する」を選択します
  - ここで「ユーザーデータフォルダーに構成を追加する」を選ぶと、プロジェクトに `.devcontainer/` ディレクトリが作成されず、ユーザーデータフォルダーに設定が保存されます。
- テンプレートを選択します
  - 例えば「Python 3」を選ぶと、Pythonの開発環境がセットアップされます。
  - python with poetry を選ぶと、Poetryを使ったPython開発環境がセットアップされます。 
- インストールする追加機能を選択します
  - 必要なVS Code拡張機能を選ぶことができます。
- Dockerコンテナのビルドと起動が開始されます。初回はイメージのダウンロードや依存関係のインストールに時間がかかります。

### `devcontainer.json` がある場合

ワークスペースを開くとすぐに「Dev Container を開く」ボタンが表示されるので、これをクリックすればDev Container が起動します。

## その他のコマンド

Dev Containers に関するコマンドパレットから実行可能なコマンドのうち、よく使うものを紹介します。

- `Dev Containers: Rebuild Container`
  - コンテナを再ビルドします。Dockerfileやdevcontainer.jsonの変更を反映させるために使用します。
- `Dev Containers: Reopen in Container`
  - 現在 VS Code で開いているフォルダを Dev Container 内で開き直します。
- `Dev Containers: Open Folder in Container`
  - 別のフォルダを Dev Container 内で開きます。
- `Dev Containers: Open Workspace in Container`
  - 別のワークスペースを Dev Container 内で開きます。