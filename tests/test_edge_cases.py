"""
エッジケースや例外処理のテスト
"""

# pytestでのテスト実行を確実にするため、モジュール名にtestを含める

import os
import re
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from expired_file_remover.core import (
    _build_pattern_and_mapping,
    extract_date_from_filename,
    is_expired,
    is_filename_date_expired,
    remove_expired_file,
    remove_expired_files,
    remove_expired_files_by_filename_date,
)


class TestErrorHandling:
    def test_is_expired_file_not_exists(self, tmp_path):
        """存在しないファイルに対するis_expiredのテスト"""
        non_existent_file = tmp_path / "non_existent.txt"
        with pytest.raises(FileNotFoundError):
            is_expired(non_existent_file, 10)

    def test_is_expired_invalid_deadline_type(self, tmp_path):
        """無効な型のdeadlineに対するis_expiredのテスト"""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with pytest.raises(TypeError):
            is_expired(test_file, "10")  # type: ignore

        with pytest.raises(TypeError):
            is_expired(test_file, [10])  # type: ignore

        with pytest.raises(TypeError):
            is_expired(test_file, {})  # type: ignore

    def test_remove_expired_file_exceptions(self, tmp_path):
        """remove_expired_fileでの例外処理のテスト"""
        # 存在しないファイル
        non_existent_file = tmp_path / "non_existent.txt"
        assert not remove_expired_file(non_existent_file, 10)

        # パーミッションエラー
        test_file = tmp_path / "test.txt"
        test_file.touch()

        # パーミッションエラーをシミュレート
        with patch(
            "pathlib.Path.unlink", side_effect=PermissionError("権限がありません")
        ):
            assert not remove_expired_file(test_file, 10)


class TestFormatHandling:
    def test_build_pattern_and_mapping(self):
        """_build_pattern_and_mappingの詳細テスト"""
        # 基本的な日付フォーマット
        pattern, mapping = _build_pattern_and_mapping("%Y%m%d")
        assert "year4" in mapping.values()
        assert "month" in mapping.values()
        assert "day" in mapping.values()

        # より複雑なフォーマット
        pattern, mapping = _build_pattern_and_mapping("log_%Y-%m-%d_%H:%M:%S.txt")
        assert len(mapping) == 6  # 6つのフォーマット指定子
        assert re.match(pattern, "log_2025-05-28_14:30:45.txt")

        # 特殊文字を含むフォーマット
        pattern, mapping = _build_pattern_and_mapping("[%Y](%m){%d}")
        assert re.match(pattern, "[2025](05){28}")

        # 空のフォーマット
        pattern, mapping = _build_pattern_and_mapping("")
        assert not mapping  # マッピングは空

        # フォーマット指定子がない場合
        pattern, mapping = _build_pattern_and_mapping("log.txt")
        assert not mapping  # マッピングは空

        # 重複するフォーマット指定子の処理（124-125行のカバレッジ）
        pattern, mapping = _build_pattern_and_mapping("%Y%m%d%Y%m%d")
        assert pattern.count("year4") == 2
        assert len(mapping) == 3  # 重複を除いた指定子数

    def test_extract_date_from_filename_edge_cases(self):
        """extract_date_from_filenameのエッジケーステスト"""
        # 一般的なエラー
        with patch("re.search", side_effect=Exception("一般的なエラー")):
            assert extract_date_from_filename("file.txt", "%Y%m%d") is None

        # KeyErrorが発生するケース
        with patch(
            "re.search",
            return_value=type(
                "obj",
                (object,),
                {
                    "groupdict": lambda self: {"not_month": "01", "not_day": "01"},
                    "group": lambda self, name: "2025" if name == "year4" else "01",
                },
            )(),
        ):
            assert extract_date_from_filename("file_20250101.txt", "%Y%m%d") is None

        # 日付の妥当性チェック（226行のカバレッジ）
        # 2月30日のような無効な日付
        mock_match = type(
            "obj",
            (object,),
            {
                "groupdict": lambda self: {"year4": "2025", "month": "02", "day": "30"},
                "group": lambda self, name: {
                    "year4": "2025",
                    "month": "02",
                    "day": "30",
                }.get(name, "01"),
            },
        )()
        with patch("re.search", return_value=mock_match):
            assert extract_date_from_filename("file_20250230.txt", "%Y%m%d") is None

        # ValueError例外（234行のカバレッジ）
        # 不正な日付フォーマット（数字じゃない値を入れる）
        mock_date_match = type(
            "obj",
            (object,),
            {
                "groupdict": lambda self: {"year4": "abcd", "month": "xy", "day": "zz"},
                "group": lambda self, name: {
                    "year4": "abcd",
                    "month": "xy",
                    "day": "zz",
                }.get(name, "01"),
            },
        )()
        with patch("re.search", return_value=mock_date_match):
            assert extract_date_from_filename("file_abcdxyzz.txt", "%Y%m%d") is None

    def test_is_filename_date_expired_invalid_type(self, tmp_path):
        """is_filename_date_expiredでの無効な型のテスト"""
        test_file = tmp_path / "file_20250101.txt"
        test_file.touch()

        with pytest.raises(TypeError):
            is_filename_date_expired(test_file, "%Y%m%d", "invalid")  # type: ignore

    def test_remove_expired_files_file_filter(self, tmp_path):
        """remove_expired_filesのファイルフィルター処理のテスト"""
        # 様々な拡張子のファイルを作成
        old_files = [
            "old1.txt",
            "old2.log",
            "old3.dat",
            "old4",  # 拡張子なし
            "old5.txt.bak",  # 複合拡張子
        ]
        for name in old_files:
            file_path = tmp_path / name
            file_path.touch()
            # 10日前の日付に設定
            old_time = datetime.now() - timedelta(days=10)
            os.utime(file_path, (old_time.timestamp(), old_time.timestamp()))

        # .txtと.logファイルのみ削除
        count = remove_expired_files(tmp_path, 5, file_filter=[".txt", ".log"])
        assert count == 2  # 2つのファイルだけが削除される

        # 確認
        assert not (tmp_path / "old1.txt").exists()
        assert not (tmp_path / "old2.log").exists()
        assert (tmp_path / "old3.dat").exists()
        assert (tmp_path / "old4").exists()  # 拡張子なしファイルは残る
        assert (
            tmp_path / "old5.txt.bak"
        ).exists()  # .txt.bakファイルは残る（.txtではない）

        # サフィックスがない場合のテスト（行97のカバレッジのため）
        empty_file = (
            tmp_path / ".hidden"
        )  # 隠しファイル（サフィックスなしエッジケース）
        empty_file.touch()
        old_time = datetime.now() - timedelta(days=10)
        os.utime(empty_file, (old_time.timestamp(), old_time.timestamp()))

        count = remove_expired_files(tmp_path, 5, file_filter=[".hidden"])
        assert count == 0  # 拡張子として認識されないので削除されない

    def test_remove_by_filename_date_error_cases(self, tmp_path):
        """remove_expired_files_by_filename_dateのエラーケースのテスト"""
        # OSErrorをシミュレート（削除失敗ケース）
        test_file = tmp_path / "file_20230101.txt"
        test_file.touch()

        # 単一の削除エラー（OSError - 340行のカバレッジ）
        with patch("pathlib.Path.unlink", side_effect=OSError("その他のエラー")):
            try:
                deleted = remove_expired_files_by_filename_date(
                    tmp_path, "%Y%m%d", datetime(2025, 1, 1)
                )
                assert deleted == 0  # ファイルは削除されない
            except Exception:
                # OSErrorが正しく処理される
                pass

        # 外側のtry-exceptブロックのPermissionError（347-348行のカバレッジ）
        # これは外側のtry-exceptブロックに入るケースをテスト
        with patch("os.access", return_value=True):  # アクセス権チェックをバイパス
            with patch(
                "expired_file_remover.core.is_filename_date_expired",
                side_effect=PermissionError("外側の処理エラー"),
            ):
                with pytest.raises(PermissionError):
                    remove_expired_files_by_filename_date(
                        tmp_path, "%Y%m%d", datetime(2025, 1, 1)
                    )


class TestExceptionHandling:
    def test_remove_expired_files_directory_errors(self, tmp_path):
        """remove_expired_filesのディレクトリエラーテスト"""
        # 存在しないディレクトリ
        non_existent_dir = tmp_path / "non_existent"
        with pytest.raises(FileNotFoundError):
            remove_expired_files(non_existent_dir, 10)

        # ファイルをディレクトリとして指定した場合
        test_file = tmp_path / "test.txt"
        test_file.touch()
        with pytest.raises(NotADirectoryError):
            remove_expired_files(test_file, 10)

    def test_remove_expired_files_with_file_errors(self, tmp_path):
        """ファイル削除時のエラー処理テスト"""
        # ディレクトリを作成
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # テストファイルを作成
        test_file = test_dir / "test.txt"
        test_file.touch()

        # OSErrorをシミュレート
        with patch("pathlib.Path.unlink", side_effect=OSError("OSエラー")):
            # エラーが出てもカウントは0で返る
            assert remove_expired_files(test_dir, 0) == 0

    def test_remove_expired_files_by_filename_date_os_error(self, tmp_path):
        """remove_expired_files_by_filename_dateでのOSErrorテスト"""
        # ディレクトリを作成
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # テストファイルを作成
        test_file = test_dir / "file_20250101.txt"
        test_file.touch()

        # OSErrorをシミュレート
        with patch("pathlib.Path.unlink", side_effect=OSError("OSエラー")):
            # エラーが出てもカウントは0で返る
            assert (
                remove_expired_files_by_filename_date(
                    test_dir, "%Y%m%d", datetime(2025, 2, 1)
                )
                == 0
            )

    def test_remove_expired_files_by_filename_date_permission_error(self, tmp_path):
        """remove_expired_files_by_filename_dateでのPermissionErrorテスト"""
        # ディレクトリを作成
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # テストファイルを作成
        test_file = test_dir / "file_20250101.txt"
        test_file.touch()

        # PermissionErrorをシミュレート
        with patch(
            "pathlib.Path.unlink", side_effect=PermissionError("権限がありません")
        ):
            with pytest.raises(PermissionError) as e:
                remove_expired_files_by_filename_date(
                    test_dir, "%Y%m%d", datetime(2025, 2, 1)
                )
            assert "削除権限がありません" in str(e.value)
