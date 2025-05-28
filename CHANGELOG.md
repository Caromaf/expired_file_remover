# Changelog

このプロジェクトのすべての重要な変更はこのファイルに記載されます。

形式は [Keep a Changelog](https://keepachangelog.com/ja/1.0.0/) に基づいています。

## [0.1.0] - 2025-05-28

### 追加

- 初期リリース
- `remove_expired_file` 関数 - 単一ファイルの削除
- `remove_expired_files` 関数 - ディレクトリ内の複数ファイルの削除
- `is_expired` 関数 - ファイルが期限切れかどうかの判定
- 以下の期限指定方法をサポート:
  - 整数 (日数)
  - `datetime` オブジェクト (特定の日時)
  - `timedelta` オブジェクト (現在からの時間差)
- 再帰的処理オプション
- ファイル拡張子フィルターオプション