---
sidebar_position: 1
slug: /intro
---

# expired-file-remover 入門

`expired-file-remover`は特定のディレクトリ内で作成・更新から一定期間を経過したファイルを削除するためのPythonパッケージです。

## 特徴

- 指定された日数、datetime、timedelta に基づいて古いファイルを削除
- 単一ファイルまたはディレクトリ内の全ファイルを処理可能
- 再帰的に処理するオプション（サブディレクトリも含む）
- ファイル拡張子によるフィルタリング機能
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

詳細な使い方については [README.md](https://github.com/your-organization/expired-file-remover) を参照してください。
