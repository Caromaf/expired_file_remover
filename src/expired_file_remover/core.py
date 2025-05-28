"""
エクスパイア（有効期限切れ）したファイルを削除するモジュール
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Pattern, Union


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


def extract_date_from_filename(
    filename: str, date_format: str
) -> Optional[datetime]:
    """
    ファイル名から日付を抽出します

    Args:
        filename: 日付を抽出するファイル名
        date_format: 日付のフォーマット（例: '%Y%m%d', '%Y-%m-%d'）
            - %Y: 年を4桁で表示（例: 2025）
            - %m: 月を2桁で表示（例: 05）
            - %d: 日を2桁で表示（例: 28）
            - その他のフォーマットについてはPythonのdatetimeモジュールの
              strptimeメソッドのドキュメントを参照してください

    Returns:
        Optional[datetime]: 抽出された日付。抽出できない場合はNone
    """
    # 日付フォーマットに含まれるフォーマット指定子を取得
    format_specifiers = re.findall(r'%[YymdHMS]', date_format)
    if not format_specifiers:
        raise ValueError(f"日付フォーマット '{date_format}' に有効な日付指定子がありません")

    # フォーマット文字列をパースしやすい正規表現に変換
    regex_pattern = date_format
    for specifier in ['%Y', '%m', '%d', '%H', '%M', '%S', '%y']:
        if specifier in regex_pattern:
            if specifier == '%Y':
                regex_pattern = regex_pattern.replace(specifier, r'(\d{4})')
            elif specifier in ['%m', '%d', '%H', '%M', '%S']:
                regex_pattern = regex_pattern.replace(specifier, r'(\d{2})')
            elif specifier == '%y':
                regex_pattern = regex_pattern.replace(specifier, r'(\d{2})')

    # 正規表現で検索できるように特殊文字をエスケープ
    regex_pattern = re.escape(regex_pattern).replace('\\(', '(').replace('\\)', ')')

    # ファイル名から日付部分を抽出
    match = re.search(regex_pattern, filename)
    if not match:
        return None

    try:
        # 抽出した文字列を日付として解析
        date_string = ""
        current_pos = 0
        for specifier in format_specifiers:
            specifier_pos = date_format.find(specifier, current_pos)
            if specifier_pos >= 0:
                date_string += date_format[current_pos:specifier_pos]
                date_string += match.group(format_specifiers.index(specifier) + 1)
                current_pos = specifier_pos + len(specifier)

        # 最後の部分を追加
        date_string += date_format[current_pos:]

        # 日付文字列をパース
        return datetime.strptime(date_string, date_format)
    except (ValueError, IndexError):
        return None


def remove_expired_files_by_filename_date(
    dir_path: Union[str, Path],
    date_format: str,
    deadline: Union[datetime, timedelta, int],
    recursive: bool = False,
    file_filter: Optional[List[str]] = None,
) -> int:
    """
    ファイル名に含まれる日付に基づいて、期限切れファイルを削除します

    Args:
        dir_path: 削除対象ディレクトリのパス
        date_format: ファイル名の日付フォーマット（例: '%Y%m%d', '%Y-%m-%d'）
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

    # ディレクトリ内のファイルを処理
    glob_pattern = "**/*" if recursive else "*"

    # deadlineを日付として標準化
    deadline_date: datetime
    if isinstance(deadline, datetime):
        deadline_date = deadline
    elif isinstance(deadline, timedelta):
        deadline_date = datetime.now() - deadline
    elif isinstance(deadline, int):
        deadline_date = datetime.now() - timedelta(days=deadline)
    else:
        raise TypeError("deadlineはdatetime、timedelta、または整数型である必要があります")

    for item in path.glob(glob_pattern):
        # ディレクトリはスキップ
        if item.is_dir():
            continue

        # file_filter が指定されている場合、対象の拡張子のみを処理
        if file_filter is not None:
            if item.suffix and any(ext == item.suffix for ext in file_filter):
                pass  # 拡張子が一致するので処理を続行
            else:
                continue  # 拡張子が一致しないのでスキップ

        try:
            # ファイル名から日付を抽出
            file_date = extract_date_from_filename(item.name, date_format)
            if file_date and file_date < deadline_date:
                item.unlink()
                deleted_count += 1
        except (PermissionError, OSError) as e:
            print(f"ファイル {item} の削除に失敗しました: {e}")

    return deleted_count
