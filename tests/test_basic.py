"""
expired_file_removerの基本機能のテスト
"""

import os
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest

from expired_file_remover import is_expired, remove_expired_file, remove_expired_files


class TestExpiredFileRemover:
    """期限切れファイル削除機能のテストクラス"""

    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        """テスト用の一時ディレクトリを作成するフィクスチャ"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # テスト後にディレクトリを削除
        shutil.rmtree(temp_dir)

    def create_test_file(
        self, dir_path: Path, filename: str, days_old: int = 0
    ) -> Path:
        """
        テスト用ファイルを作成し、指定した日数分古い更新日時を設定する
        """
        file_path = dir_path / filename
        # ファイル作成
        with open(file_path, "w") as f:
            f.write(f"Test file {filename}")

        # 更新日時を設定
        if days_old > 0:
            old_time = datetime.now() - timedelta(days=days_old)
            old_timestamp = old_time.timestamp()
            os.utime(file_path, (old_timestamp, old_timestamp))

        return file_path

    def test_is_expired(self, temp_dir: Path) -> None:
        """is_expired関数のテスト"""
        # 10日前のファイル作成
        old_file = self.create_test_file(temp_dir, "old.txt", 10)
        # 現在のファイル作成
        new_file = self.create_test_file(temp_dir, "new.txt")

        # 異なるdeadlineタイプでのテスト
        # 整数型
        assert is_expired(old_file, 5)  # 5日より古いのでTrue
        assert not is_expired(new_file, 5)  # 5日より新しいのでFalse

        # timedelta型
        assert is_expired(old_file, timedelta(days=5))
        assert not is_expired(new_file, timedelta(days=5))

        # datetime型
        deadline = datetime.now() - timedelta(days=5)
        assert is_expired(old_file, deadline)
        assert not is_expired(new_file, deadline)

    def test_remove_expired_file(self, temp_dir: Path) -> None:
        """remove_expired_file関数のテスト"""
        old_file = self.create_test_file(temp_dir, "old.txt", 10)
        new_file = self.create_test_file(temp_dir, "new.txt")

        # 古いファイルは削除される
        assert remove_expired_file(old_file, 5)  # 5日より古いファイルを削除
        assert not old_file.exists()

        # 新しいファイルは削除されない
        assert not remove_expired_file(new_file, 5)
        assert new_file.exists()

    def test_remove_expired_files(self, temp_dir: Path) -> None:
        """remove_expired_files関数のテスト"""
        # さまざまな古さのファイルを作成
        self.create_test_file(temp_dir, "old1.txt", 20)
        self.create_test_file(temp_dir, "old2.txt", 15)
        self.create_test_file(temp_dir, "old3.log", 10)
        self.create_test_file(temp_dir, "new1.txt", 3)
        self.create_test_file(temp_dir, "new2.log", 1)

        # サブディレクトリにファイルを作成
        sub_dir = temp_dir / "subdir"
        sub_dir.mkdir()
        self.create_test_file(sub_dir, "sub_old.txt", 12)
        self.create_test_file(sub_dir, "sub_new.txt", 2)

        # 7日より古いファイルを削除
        count = remove_expired_files(temp_dir, 7)
        # サブディレクトリは対象外なので3つのファイルが削除される
        assert count == 3

        # ファイルが正しく削除されたか確認
        assert not (temp_dir / "old1.txt").exists()
        assert not (temp_dir / "old2.txt").exists()
        assert not (temp_dir / "old3.log").exists()
        assert (temp_dir / "new1.txt").exists()
        assert (temp_dir / "new2.log").exists()
        assert (
            sub_dir / "sub_old.txt"
        ).exists()  # サブディレクトリ内なので削除されない
        assert (sub_dir / "sub_new.txt").exists()

        # フィルタ指定のテスト（.logファイルのみ）
        # 別の古いlogファイルを作成して、これを削除対象とする
        self.create_test_file(temp_dir, "old4.log", 3)
        count = remove_expired_files(temp_dir, 2, file_filter=[".log"])
        assert count == 1  # old4.logのみ削除される
        assert (temp_dir / "new1.txt").exists()
        assert (temp_dir / "new2.log").exists()
        assert not (temp_dir / "old4.log").exists()

        # 再帰的削除のテスト
        count = remove_expired_files(temp_dir, 7, recursive=True)
        assert count == 1  # サブディレクトリ内のsub_old.txtが削除される
        assert not (sub_dir / "sub_old.txt").exists()
        assert (sub_dir / "sub_new.txt").exists()
