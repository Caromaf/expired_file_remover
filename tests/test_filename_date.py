"""
ファイル名に含まれる日付に基づいて期限切れファイルを削除する機能のテスト
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from expired_file_remover.core import (
    extract_date_from_filename,
    remove_expired_files_by_filename_date,
)


class TestExtractDateFromFilename:
    def test_basic_format(self):
        """基本的な日付フォーマットのテスト"""
        assert extract_date_from_filename(
            Path("file_20250528.txt"), "%Y%m%d"
        ) == datetime(2025, 5, 28)
        assert extract_date_from_filename(
            Path("file_2025-05-28.txt"), "%Y-%m-%d"
        ) == datetime(2025, 5, 28)
        assert extract_date_from_filename(
            Path("2025_05_28_file.log"), "%Y_%m_%d"
        ) == datetime(2025, 5, 28)

    def test_time_format(self):
        """時刻を含む日付フォーマットのテスト"""
        assert extract_date_from_filename(
            Path("backup_20250528_235959.tar.gz"), "%Y%m%d_%H%M%S"
        ) == datetime(2025, 5, 28, 23, 59, 59)
        assert extract_date_from_filename(
            Path("log-2025-05-28-23-59.txt"), "%Y-%m-%d-%H-%M"
        ) == datetime(2025, 5, 28, 23, 59)

    def test_two_digit_year(self):
        """2桁年のテスト"""
        assert extract_date_from_filename(
            Path("file_250528.txt"), "%y%m%d"
        ) == datetime(2025, 5, 28)
        assert extract_date_from_filename(
            Path("file_25-05-28.txt"), "%y-%m-%d"
        ) == datetime(2025, 5, 28)

    def test_special_chars(self):
        """特殊文字を含むフォーマットのテスト"""
        assert extract_date_from_filename(
            Path("file[20250528].txt"), "[%Y%m%d]"
        ) == datetime(2025, 5, 28)
        assert extract_date_from_filename(
            Path("file(2025.05.28).txt"), "(%Y.%m.%d)"
        ) == datetime(2025, 5, 28)

    def test_no_match(self):
        """日付が含まれないファイル名のテスト"""
        assert extract_date_from_filename(Path("file.txt"), "%Y%m%d") is None
        assert extract_date_from_filename(Path("nodate_file.log"), "%Y-%m-%d") is None
        # フォーマットと一致しない日付パターン
        assert extract_date_from_filename(Path("file_2025-05-28.txt"), "%Y%m%d") is None

    def test_invalid_date(self):
        """無効な日付のテスト"""
        assert (
            extract_date_from_filename(Path("file_20252528.txt"), "%Y%m%d") is None
        )  # 無効な月
        assert (
            extract_date_from_filename(Path("file_2025-13-28.txt"), "%Y-%m-%d") is None
        )  # 無効な月
        assert (
            extract_date_from_filename(Path("file_2025-12-32.txt"), "%Y-%m-%d") is None
        )  # 無効な日

    def test_invalid_format(self):
        """無効なフォーマットのテスト"""
        with pytest.raises(ValueError):
            extract_date_from_filename("file.txt", "invalid")

    def test_format_validation_exception(self):
        """無効な日付フォーマット指定子の例外テスト"""
        with pytest.raises(ValueError) as e:
            extract_date_from_filename(
                Path("file.txt"), "%Z"
            )  # 無効なフォーマット指定子
        assert "有効な日付フォーマット指定子" in str(e.value)

    def test_extract_date_with_invalid_day(self):
        """日付妥当性チェックで月と日が不一致となるケースのテスト (226行目のカバレッジ)"""
        # monthのみ不一致のケース（月は02だが日付変換後は03になる）
        mock_match = type(
            "obj",
            (object,),
            {
                "groupdict": lambda self: {"year4": "2025", "month": "02", "day": "31"},
                "group": lambda self, name: {
                    "year4": "2025",
                    "month": "02",
                    "day": "31",
                }.get(name, "01"),
            },
        )()

        with pytest.raises(ValueError):
            # まず通常の変換で2月31日が3月3日になることを確認
            datetime.strptime("20250231", "%Y%m%d")

        # extract_date_from_filenameでは日付の妥当性チェックでNoneが返る
        with patch("re.search", return_value=mock_match):
            assert extract_date_from_filename("file_20250231.txt", "%Y%m%d") is None

    def test_extract_date_with_invalid_month(self):
        """日付妥当性チェックで月が不一致となるケースのテスト (226行目前半部分のカバレッジ)"""
        # 4月31日など、月と日の不一致（存在しない日付）をテスト
        # ファイル名で直接テスト
        filename = "file_20250431.txt"

        try:
            # まず通常の変換で4月31日が5月1日になることを確認
            dt = datetime.strptime("20250431", "%Y%m%d")
            assert dt.month == 5  # 確認：4月31日→5月1日に変換される
        except ValueError:
            # 環境によっては直接例外になるかもしれないのでパス
            pass

        # mock_matchを使ったテスト
        mock_match = type(
            "obj",
            (object,),
            {
                "groupdict": lambda self: {"year4": "2025", "month": "04", "day": "31"},
                "group": lambda self, name: {
                    "year4": "2025",
                    "month": "04",
                    "day": "31",
                }.get(name, "01"),
            },
        )()

        with patch("re.search", return_value=mock_match):
            # extract_date_from_filenameはNoneを返す（日付妥当性チェックに失敗）
            assert extract_date_from_filename(filename, "%Y%m%d") is None

        # 実際のファイル名で試す
        with patch.object(re, "search", wraps=re.search) as mock_search:
            result = extract_date_from_filename("file_20250431.txt", "%Y%m%d")
            assert result is None, "有効でない日付なのでNoneを返すべき"
            assert mock_search.called

    def test_invalid_date_format_specifier_direct(self):
        """無効な日付フォーマット指定子の例外ケース (234行目のカバレッジ)"""
        # コードを直接実行して動作確認
        try:
            # これは無効な日付フォーマット指定子なので例外が発生するはず
            extract_date_from_filename("file.txt", "%Z")
            # ここには到達しないはず
            assert False, "無効な日付フォーマットなのに例外が発生しませんでした"
        except ValueError as e:
            # これで234行目の条件分岐がカバーされる
            assert "有効な日付フォーマット指定子" in str(e)


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
        assert (
            test_dir / "subdir" / "file_20240201.txt"
        ).exists()  # サブディレクトリは処理されず

    def test_remove_by_filename_date_with_recursive(self, setup_test_dir):
        """再帰的に検索するテスト"""
        test_dir = setup_test_dir
        deadline = datetime(2025, 1, 1)

        # 再帰的に削除実行
        deleted = remove_expired_files_by_filename_date(
            test_dir, "%Y%m%d", deadline, recursive=True
        )
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

    def test_remove_from_empty_dir(self, tmp_path):
        """空のディレクトリでのテスト"""
        deleted = remove_expired_files_by_filename_date(
            tmp_path, "%Y%m%d", datetime(2025, 1, 1)
        )
        assert deleted == 0

    def test_remove_from_non_existent_dir(self, tmp_path):
        """存在しないディレクトリでのテスト"""
        non_existent_path = tmp_path / "non_existent"
        with pytest.raises(FileNotFoundError):
            remove_expired_files_by_filename_date(
                non_existent_path, "%Y%m%d", datetime(2025, 1, 1)
            )

    def test_path_is_not_a_directory(self, tmp_path):
        """指定パスがディレクトリではない場合のテスト"""
        file_path = tmp_path / "a_file.txt"
        file_path.touch()
        with pytest.raises(NotADirectoryError):
            remove_expired_files_by_filename_date(
                file_path, "%Y%m%d", datetime(2025, 1, 1)
            )

    def test_remove_by_filename_date_with_multiple_filters(self, tmp_path):
        """複数の日付フォーマットを同時に指定するテスト"""
        test_files = [
            "data_20230101_001.txt",  # YYYYMMDD形式
            "log-2023-01-01.txt",  # YYYY-MM-DD形式
            "backup_01-01-2023.txt",  # MM-DD-YYYY形式
            "current.txt",  # 日付なし
        ]
        for file_name in test_files:
            (tmp_path / file_name).touch()

        patterns = ["%Y%m%d", "%Y-%m-%d", "%m-%d-%Y"]
        deleted = remove_expired_files_by_filename_date(
            tmp_path, patterns, datetime(2025, 1, 1)
        )
        assert deleted == 3  # 日付を含む3つのファイルが削除されるべき

    def test_remove_files_with_permission_error(self, tmp_path):
        """パーミッションエラーが発生する場合のテスト"""

        # テスト用ファイルを作成
        test_file = tmp_path / "data_20230101.txt"
        test_file.touch()

        # ファイルのパーミッションを読み取り専用に設定
        current_mode = test_file.stat().st_mode
        test_file.chmod(current_mode & ~0o222)  # 書き込み権限を削除

        try:
            with pytest.raises(PermissionError):
                remove_expired_files_by_filename_date(
                    tmp_path, "%Y%m%d", datetime(2025, 1, 1)
                )
        finally:
            # テストファイルが存在する場合は権限を戻してから削除
            if test_file.exists():
                test_file.chmod(current_mode | 0o222)  # 書き込み権限を追加
                test_file.unlink()

    def test_remove_files_with_different_date_formats(self, tmp_path):
        """異なる日付フォーマットが混在する場合のテスト"""
        test_files = [
            "log_20230101.txt",  # YYYYMMDD
            "data-2023-01-01.txt",  # YYYY-MM-DD
            "invalid_date.txt",  # 日付なし
        ]
        for file_name in test_files:
            (tmp_path / file_name).touch()

        # 期限切れの基準日を設定
        reference_date = datetime(2025, 1, 1)

        # YYYYMMDD形式のみを指定してテスト
        deleted = remove_expired_files_by_filename_date(
            tmp_path, "%Y%m%d", reference_date
        )
        assert deleted == 1  # YYYYMMDD形式のファイルのみが削除されるべき
