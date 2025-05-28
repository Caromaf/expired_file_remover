"""
エクスパイア（有効期限切れ）したファイルを削除するモジュール
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Union


def is_expired(file_path: Path, deadline: Union[datetime, timedelta, int]) -> bool:
    """
    ファイルが期限切れかどうかを判定します

    Args:
        file_path: 判定対象ファイルのパス
        deadline: 期限を示すデータ
            - datetime型: この日時より前に更新されたファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前に更新されたファイルは期限切れと判定
            - int型: 現在日からこの日数より前に更新されたファイルは期限切れと判定

    Returns:
        bool: ファイルが期限切れの場合はTrue、そうでない場合はFalse
    """
    if not file_path.exists():
        raise FileNotFoundError(f"ファイルが存在しません: {file_path}")

    # ファイルの最終更新時刻を取得
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

    # deadlineの型に応じて判定方法を変える
    if isinstance(deadline, datetime):
        return mtime < deadline
    elif isinstance(deadline, timedelta):
        return mtime < datetime.now() - deadline
    elif isinstance(deadline, int):
        return mtime < datetime.now() - timedelta(days=deadline)
    else:
        raise TypeError(
            "deadlineはdatetime、timedelta、または整数型である必要があります"
        )


def remove_expired_file(
    file_path: Union[str, Path], deadline: Union[datetime, timedelta, int]
) -> bool:
    """
    指定された期限より古いファイルを削除します

    Args:
        file_path: 削除対象ファイルのパス
        deadline: 期限を示すデータ
            - datetime型: この日時より前に更新されたファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前に更新されたファイルは期限切れと判定
            - int型: 現在日からこの日数より前に更新されたファイルは期限切れと判定

    Returns:
        bool: 削除に成功した場合はTrue、そうでない場合はFalse
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path

    try:
        if is_expired(path, deadline):
            path.unlink()
            return True
        return False
    except (FileNotFoundError, PermissionError) as e:
        print(f"エラー: {e}")
        return False


def remove_expired_files(
    dir_path: Union[str, Path],
    deadline: Union[datetime, timedelta, int],
    recursive: bool = False,
    file_filter: Optional[List[str]] = None,
) -> int:
    """
    指定されたディレクトリ内の期限切れファイルをすべて削除します

    Args:
        dir_path: 削除対象ディレクトリのパス
        deadline: 期限を示すデータ
            - datetime型: この日時より前に更新されたファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前に更新されたファイルは期限切れと判定
            - int型: 現在日からこの日数より前に更新されたファイルは期限切れと判定
        recursive: サブディレクトリも対象とするかどうか (デフォルト: False)
        file_filter: 対象とするファイル拡張子のリスト (例: ['.txt', '.log'])

    Returns:
        int: 削除されたファイルの数
    """
    path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    if not path.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"指定されたパスはディレクトリではありません: {path}")

    deleted_count = 0

    # ディレクトリ内のファイルを処理
    glob_pattern = "**/*" if recursive else "*"

    for item in path.glob(glob_pattern):
        # ディレクトリはスキップ
        if item.is_dir():
            continue

        # file_filter が指定されている場合、対象の拡張子のみを処理
        if file_filter is not None:
            # テストのために、拡張子比較の前にドットがあることを確認
            if item.suffix and any(ext == item.suffix for ext in file_filter):
                pass  # 拡張子が一致するので処理を続行
            else:
                continue  # 拡張子が一致しないのでスキップ

        try:
            if is_expired(item, deadline):
                item.unlink()
                deleted_count += 1
        except (PermissionError, OSError) as e:
            print(f"ファイル {item} の削除に失敗しました: {e}")

    return deleted_count


def extract_date_from_filename(file_path: Path, date_format: str) -> Optional[datetime]:
    """
    ファイル名から日付を抽出します

    Args:
        file_path: 対象ファイルのパス
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d', '%Y%m%d_%H%M%S'）

    Returns:
        Optional[datetime]: 抽出された日付。抽出できない場合はNone
    """
    try:
        filename = file_path.stem

        # 日付フォーマット文字列から正規表現パターンを構築
        format_to_pattern = {
            "%Y": r"(?P<Y>\d{4})",  # 年（4桁）
            "%y": r"(?P<y>\d{2})",  # 年（2桁）
            "%m": r"(?P<m>\d{2})",  # 月（2桁）
            "%d": r"(?P<d>\d{2})",  # 日（2桁）
            "%H": r"(?P<H>\d{2})",  # 時（24時間制）
            "%I": r"(?P<I>\d{2})",  # 時（12時間制）
            "%M": r"(?P<M>\d{2})",  # 分
            "%S": r"(?P<S>\d{2})",  # 秒
        }

        # エスケープが必要な文字
        special_chars = ".^$*+?{}[]|()"

        # 正規表現パターンを構築
        pattern = date_format
        for fmt, regex in format_to_pattern.items():
            pattern = pattern.replace(fmt, regex)

        # 日付フォーマット中の特殊文字をエスケープ
        for char in special_chars:
            escaped = "\\" + char
            pattern = pattern.replace(char, escaped)

        # ファイル名から日付部分を検索
        match = re.search(pattern, filename)
        if not match:
            return None

        # マッチした部分から日付文字列を再構成
        date_components = {}
        for key, value in match.groupdict().items():
            if key in ("Y", "y", "m", "d", "H", "I", "M", "S"):
                date_components[key] = value

        # 日付文字列を再構成
        date_str = date_format
        for fmt, regex in format_to_pattern.items():
            key = regex[3:4]  # '(?P<Y>...)' から 'Y' を取得
            if key in date_components:
                date_str = date_str.replace(fmt, date_components[key])

        # 日付文字列をdatetimeオブジェクトに変換
        return datetime.strptime(date_str, date_format)

    except (ValueError, KeyError) as e:
        return None


def is_filename_date_expired(
    file_path: Path, date_format: str, deadline: Union[datetime, timedelta, int]
) -> bool:
    """
    ファイル名の日付が期限切れかどうかを判定します

    Args:
        file_path: 判定対象ファイルのパス
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d'）
        deadline: 期限を示すデータ
            - datetime型: この日時より前の日付を持つファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前の日付を持つファイルは期限切れと判定
            - int型: 現在日からこの日数より前の日付を持つファイルは期限切れと判定

    Returns:
        bool: ファイルが期限切れの場合はTrue、そうでない場合はFalse
    """
    file_date = extract_date_from_filename(file_path, date_format)
    if file_date is None:
        return False

    if isinstance(deadline, datetime):
        return file_date < deadline
    elif isinstance(deadline, timedelta):
        return file_date < datetime.now() - deadline
    elif isinstance(deadline, int):
        return file_date < datetime.now() - timedelta(days=deadline)
    else:
        raise TypeError(
            "deadlineはdatetime、timedelta、または整数型である必要があります"
        )


def remove_expired_files_by_filename_date(
    dir_path: Union[str, Path],
    date_format: str,
    deadline: Union[datetime, timedelta, int],
    recursive: bool = False,
    file_filter: Optional[List[str]] = None,
) -> int:
    """
    ファイル名の日付を基準に、指定されたディレクトリ内の期限切れファイルをすべて削除します

    Args:
        dir_path: 削除対象ディレクトリのパス
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d'）
        deadline: 期限を示すデータ
            - datetime型: この日時より前の日付を持つファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前の日付を持つファイルは期限切れと判定
            - int型: 現在日からこの日数より前の日付を持つファイルは期限切れと判定
        recursive: サブディレクトリも対象とするかどうか (デフォルト: False)
        file_filter: 対象とするファイル拡張子のリスト (例: ['.txt', '.log'])

    Returns:
        int: 削除されたファイルの数
    """
    path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    if not path.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"指定されたパスはディレクトリではありません: {path}")

    deleted_count = 0
    glob_pattern = "**/*" if recursive else "*"

    for item in path.glob(glob_pattern):
        if item.is_dir():
            continue

        if file_filter is not None:
            if item.suffix and any(ext == item.suffix for ext in file_filter):
                pass
            else:
                continue

        try:
            if is_filename_date_expired(item, date_format, deadline):
                item.unlink()
                deleted_count += 1
        except (PermissionError, OSError) as e:
            print(f"ファイル {item} の削除に失敗しました: {e}")

    return deleted_count
