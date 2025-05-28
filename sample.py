#!/usr/bin/env python
"""
expired-file-remover のサンプルスクリプト
"""
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from expired_file_remover import is_expired, remove_expired_file, remove_expired_files


def main():
    """サンプルコードを実行します"""
    print("expired-file-remover サンプルスクリプト")

    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"一時ディレクトリを作成しました: {temp_path}")

        # テストファイルを作成
        files = []
        for i in range(5):
            file_path = temp_path / f"test_file_{i}.txt"
            with open(file_path, "w") as f:
                f.write(f"テストファイル {i}")
            files.append(file_path)
            print(f"ファイル作成: {file_path}")

        # サブディレクトリを作成
        sub_dir = temp_path / "subdir"
        sub_dir.mkdir()

        # サブディレクトリ内にファイルを作成
        sub_files = []
        for i in range(3):
            file_path = sub_dir / f"sub_file_{i}.log"
            with open(file_path, "w") as f:
                f.write(f"サブディレクトリ内テストファイル {i}")
            sub_files.append(file_path)
            print(f"サブディレクトリ内ファイル作成: {file_path}")

        # 一部のファイルのタイムスタンプを更新（古いファイル）
        old_time = datetime.now() - timedelta(days=10)
        old_timestamp = old_time.timestamp()

        # ファイル2と4を古いファイルに設定
        for i in [1, 3]:
            os.utime(files[i], (old_timestamp, old_timestamp))
            print(f"ファイル {files[i]} のタイムスタンプを10日前に設定")

        # サブディレクトリのファイル1を古いファイルに設定
        os.utime(sub_files[0], (old_timestamp, old_timestamp))
        print(f"ファイル {sub_files[0]} のタイムスタンプを10日前に設定")

        # 各ファイルの情報を表示
        for file in files + sub_files:
            mtime = datetime.fromtimestamp(file.stat().st_mtime)
            print(f"{file}: 更新日時 = {mtime}, 期限切れ = {is_expired(file, 5)}")

        # 期限切れファイルの削除（非再帰）
        print("\n非再帰的に5日以上古いファイルを削除:")
        count = remove_expired_files(temp_path, 5)
        print(f"{count}個のファイルを削除しました")

        # 各ファイルの存在確認
        for file in files:
            print(f"{file}: 存在 = {file.exists()}")
        for file in sub_files:
            print(f"{file}: 存在 = {file.exists()}")

        # 再帰的に削除
        print("\n再帰的に5日以上古いファイルを削除:")
        count = remove_expired_files(temp_path, 5, recursive=True)
        print(f"{count}個のファイルを削除しました")

        # 各ファイルの存在確認
        for file in files:
            print(f"{file}: 存在 = {file.exists()}")
        for file in sub_files:
            print(f"{file}: 存在 = {file.exists()}")


if __name__ == "__main__":
    import os

    main()
