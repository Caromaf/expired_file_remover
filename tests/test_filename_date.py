"""
ファイル名に含まれる日付に基づいて期限切れファイルを削除する機能のテスト
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from expired_file_remover.core import (
    extract_date_from_filename,
    remove_expired_files_by_filename_date,
)


class TestExtractDateFromFilename:
    def test_basic_format(self):
        """基本的な日付フォーマットのテスト"""
        assert extract_date_from_filename("file_20250528.txt", "%Y%m%d") == datetime(2025, 5, 28)
        assert extract_date_from_filename("file_2025-05-28.txt", "%Y-%m-%d") == datetime(2025, 5, 28)
        assert extract_date_from_filename("2025_05_28_file.log", "%Y_%m_%d") == datetime(2025, 5, 28)

    def test_no_match(self):
        """日付が含まれないファイル名のテスト"""
        assert extract_date_from_filename("file.txt", "%Y%m%d") is None
        assert extract_date_from_filename("nodate_file.log", "%Y-%m-%d") is None

    def test_invalid_date(self):
        """無効な日付のテスト"""
        assert extract_date_from_filename("file_20252528.txt", "%Y%m%d") is None  # 無効な月
        assert extract_date_from_filename("file_2025-13-28.txt", "%Y-%m-%d") is None  # 無効な月

    def test_invalid_format(self):
        """無効なフォーマットのテスト"""
        with pytest.raises(ValueError):
            extract_date_from_filename("file.txt", "invalid")


class TestRemoveExpiredFilesByFilenameDate:
    @pytest.fixture
    def setup_test_dir(self, tmp_path):
        """テスト用ディレクトリとファイルをセットアップ"""
        # 有効期限切れファイル
        (tmp_path / "file_20240101.txt").touch()
        (tmp_path / "log_2024-02-15.log").touch()
        
        # 有効期限内ファイル
        (tmp_path / "file_20250601.txt").touch()  # 未来の日付
        (tmp_path / "log_2025-06-15.log").touch()  # 未来の日付
        
        # 日付を含まないファイル
        (tmp_path / "nodate.txt").touch()
        
        # サブディレクトリ
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "file_20240201.txt").touch()
        (subdir / "log_2025-07-01.log").touch()
        
        return tmp_path

    def test_remove_by_filename_date_with_datetime(self, setup_test_dir):
        """datetime型のdeadlineでのテスト"""
        test_dir = setup_test_dir
        deadline = datetime(2025, 1, 1)  # 2025年1月1日より前の日付を持つファイルを削除
        
        # 削除実行
        deleted = remove_expired_files_by_filename_date(test_dir, "%Y%m%d", deadline)
        assert deleted == 1  # ルートディレクトリの1ファイルのみ削除
        
        # ファイルの存在確認
        assert not (test_dir / "file_20240101.txt").exists()  # 削除済み
        assert (test_dir / "file_20250601.txt").exists()  # 残存
        assert (test_dir / "nodate.txt").exists()  # 日付無しファイルは残存
        assert (test_dir / "subdir" / "file_20240201.txt").exists()  # サブディレクトリは処理されず

    def test_remove_by_filename_date_with_recursive(self, setup_test_dir):
        """再帰的に検索するテスト"""
        test_dir = setup_test_dir
        deadline = datetime(2025, 1, 1)
        
        # 再帰的に削除実行
        deleted = remove_expired_files_by_filename_date(test_dir, "%Y%m%d", deadline, recursive=True)
        assert deleted == 2  # ルートとサブディレクトリの合計2ファイルを削除
        
        # ファイルの存在確認
        assert not (test_dir / "file_20240101.txt").exists()
        assert not (test_dir / "subdir" / "file_20240201.txt").exists()
        assert (test_dir / "subdir" / "log_2025-07-01.log").exists()

    def test_remove_by_filename_date_with_filter(self, setup_test_dir):
        """ファイルフィルターのテスト"""
        test_dir = setup_test_dir
        deadline = datetime(2025, 1, 1)
        
        # .logファイルのみを対象に削除実行
        deleted = remove_expired_files_by_filename_date(
            test_dir, "%Y-%m-%d", deadline, file_filter=[".log"]
        )
        assert deleted == 1
        
        # .txtファイルは残っているはず
        assert (test_dir / "file_20240101.txt").exists()
        assert not (test_dir / "log_2024-02-15.log").exists()

    def test_remove_by_filename_date_with_timedelta(self, setup_test_dir):
        """timedelta型のdeadlineでのテスト"""
        test_dir = setup_test_dir
        # 現在から1年前より古いファイルを削除
        deadline = timedelta(days=365)
        
        # 削除実行
        deleted = remove_expired_files_by_filename_date(test_dir, "%Y%m%d", deadline)
        assert deleted == 1  # 2024年1月1日のファイルのみ削除

    def test_remove_by_filename_date_with_days(self, setup_test_dir):
        """int型のdeadlineでのテスト"""
        test_dir = setup_test_dir
        # 現在から400日前より古いファイルを削除
        deadline = 400
        
        # 削除実行
        deleted = remove_expired_files_by_filename_date(test_dir, "%Y%m%d", deadline)
        assert deleted == 1  # 2024年1月1日のファイルのみ削除
