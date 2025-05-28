---
sidebar_position: 1
slug: /intro
---

# expired-file-remover 入門

`expired-file-remover`は特定のディレクトリ内で作成・更新から一定期間を経過したファイルを削除するためのPythonパッケージです。

## 特徴

- 指定された日数、datetime、timedelta に基づいて古いファイルを削除
- 単一ファイルまたはディレクトリ内の全ファイルを処理可能
- ファイル名に含まれる日付に基づいて削除 (v0.2.0で追加)
  - 複数の日付フォーマットをサポート (YYYYMMDD, YYYY-MM-DD など)
  - カスタム日付フォーマットに対応
- 再帰的に処理するオプション（サブディレクトリも含む）
- ファイル拡張子によるフィルタリング機能
- 堅牢なエラー処理
  - パーミッションエラーの適切な処理
  - 日付の妥当性チェック
- 型ヒント完全対応

## インストール方法

```bash
pip install expired-file-remover
```

または Poetry を使用する場合：

```bash
poetry add expired-file-remover
```

## 基本的な使い方

### 更新日時に基づく削除

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

### ファイル名の日付に基づく削除 (v0.2.0以降)

```python
from expired_file_remover import remove_expired_files_by_filename_date
from datetime import datetime, timedelta

# YYYYMMDD形式の日付を持つファイルを削除
count = remove_expired_files_by_filename_date(
    "/path/to/directory",
    "%Y%m%d",
    datetime(2025, 1, 1)  # この日付より前の日付を持つファイルを削除
)

# 複数の日付フォーマットに対応
formats = ["%Y%m%d", "%Y-%m-%d", "%y%m%d"]  # YYYYMMDD, YYYY-MM-DD, YYMMDD
count = remove_expired_files_by_filename_date(
    "/path/to/directory",
    formats,
    timedelta(days=30)  # 30日より前の日付を持つファイルを削除
)

# サブディレクトリも含めて処理
count = remove_expired_files_by_filename_date(
    "/path/to/directory",
    "%Y%m%d",
    datetime(2025, 1, 1),
    recursive=True
)

# 特定の拡張子のファイルのみ処理
count = remove_expired_files_by_filename_date(
    "/path/to/directory",
    "%Y%m%d",
    datetime(2025, 1, 1),
    file_filter=[".log", ".tmp"]
)
```

サポートされている日付フォーマット：
- `%Y`: 4桁の年 (例: 2025)
- `%y`: 2桁の年 (例: 25)
- `%m`: 2桁の月 (例: 01-12)
- `%d`: 2桁の日 (例: 01-31)
- `%H`: 時 (24時間形式, 00-23)
- `%M`: 分 (00-59)
- `%S`: 秒 (00-59)

これらの指定子を組み合わせて、カスタムフォーマットを作成できます。例：
- `%Y%m%d`: 20250528
- `%Y-%m-%d`: 2025-05-28
- `%Y%m%d_%H%M%S`: 20250528_235959

詳細な使い方については [README.md](https://github.com/your-organization/expired-file-remover) を参照してください。
