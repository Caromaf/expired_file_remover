# expired-file-remover

[![Python CI](https://github.com/your-organization/expired-file-remover/actions/workflows/ci.yml/badge.svg)](https://github.com/your-organization/expired-file-remover/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/expired-file-remover.svg)](https://badge.fury.io/py/expired-file-remover)
[![Python Versions](https://img.shields.io/pypi/pyversions/expired-file-remover.svg)](https://pypi.org/project/expired-file-remover/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

特定のディレクトリ内で作成・更新から一定期間を経過したファイルを削除するためのPythonパッケージです。

## 特徴

- 指定された日数、datetime、timedelta に基づいて古いファイルを削除
- 単一ファイルまたはディレクトリ内の全ファイルを処理可能
- 再帰的に処理するオプション（サブディレクトリも含む）
- ファイル拡張子によるフィルタリング機能
- 型ヒント完全対応

## インストール

```bash
pip install expired-file-remover
```

または Poetry を使用する場合：

```bash
poetry add expired-file-remover
```

## 使い方

### 基本的な使い方

```python
from expired_file_remover import remove_expired_files
from datetime import timedelta

# 10日以上古いファイルを削除（日数指定）
count = remove_expired_files("/path/to/directory", 10)
print(f"{count}個のファイルが削除されました")

# timedeltaによる指定
count = remove_expired_files("/path/to/directory", timedelta(days=10))

# サブディレクトリも含めて処理
count = remove_expired_files("/path/to/directory", 10, recursive=True)

# 特定の拡張子のファイルのみ削除
count = remove_expired_files("/path/to/directory", 10, file_filter=[".log", ".tmp"])
```

### コマンドラインツールとして使用

パッケージには、コマンドラインから実行できるサンプルスクリプトが含まれています。

```bash
# examplesディレクトリのスクリプトを直接使用する場合
python -m examples.cleanup_old_files /path/to/directory --days 30 --recursive --extensions .log .tmp

# または、スクリプトをコピーしてカスタマイズすることも可能です
```

オプション:
- `--days`: この日数より古いファイルを削除（デフォルト: 30）
- `--recursive`: サブディレクトリも対象にする
- `--extensions`: 対象とするファイル拡張子（例: .txt .log）

### 単一ファイルの処理

```python
from expired_file_remover import remove_expired_file

# 指定したファイルが30日より古ければ削除
removed = remove_expired_file("/path/to/file.txt", 30)
if removed:
    print("ファイルが削除されました")
else:
    print("ファイルは期限内または削除に失敗しました")
```

### ファイルの期限チェックのみ

```python
from expired_file_remover import is_expired
from datetime import datetime, timedelta
from pathlib import Path

file_path = Path("/path/to/file.txt")

# 日数による判定
if is_expired(file_path, 10):
    print("ファイルは10日以上前のものです")

# 時間差による判定
if is_expired(file_path, timedelta(hours=12)):
    print("ファイルは12時間以上前のものです")

# 日時による判定
deadline = datetime(2023, 1, 1)
if is_expired(file_path, deadline):
    print("ファイルは2023年1月1日より前のものです")
```

## ライセンス

MIT

## 貢献

バグ報告や機能リクエストは GitHub の Issues にてお願いします。プルリクエストも歓迎します。
