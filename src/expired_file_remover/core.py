"""
エクスパイア（有効期限切れ）したファイルを削除するモジュール
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


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


def _build_pattern_and_mapping(date_format: str) -> Tuple[str, Dict[str, str]]:
    """
    日付フォーマット文字列から正規表現パターンと、フォーマット指定子と
    グループ名のマッピングを生成します

    Args:
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d'）

    Returns:
        Tuple[str, Dict[str, str]]:
            - 正規表現パターン
            - フォーマット指定子とグループ名のマッピング
    """
    # フォーマット指定子とそれに対応する正規表現パターン
    format_specs = {
        "%Y": (r"\d{4}", "year4"),  # 4桁年
        "%y": (r"\d{2}", "year2"),  # 2桁年
        "%m": (r"\d{2}", "month"),  # 月
        "%d": (r"\d{2}", "day"),  # 日
        "%H": (r"\d{2}", "hour24"),  # 時（24時間）
        "%I": (r"\d{2}", "hour12"),  # 時（12時間）
        "%M": (r"\d{2}", "minute"),  # 分
        "%S": (r"\d{2}", "second"),  # 秒
    }

    pattern_parts = []
    current_pos = 0
    mapping = {}

    while current_pos < len(date_format):
        found_spec = False
        # より長い指定子から先にマッチを試みる
        for spec, (regex, group_name) in sorted(
            format_specs.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if date_format.startswith(spec, current_pos):
                # フォーマット指定子を発見
                pattern_parts.append(f"(?P<{group_name}>{regex})")
                mapping[spec] = group_name
                current_pos += len(spec)
                found_spec = True
                break

        if not found_spec:
            # フォーマット指定子以外の文字はエスケープして追加
            pattern_parts.append(re.escape(date_format[current_pos]))
            current_pos += 1

    return "".join(pattern_parts), mapping


def extract_date_from_filename(
    file_path: Union[str, Path], date_format: str
) -> Optional[datetime]:
    """
    ファイル名から日付を抽出します

    Args:
        file_path: 対象ファイルのパス（文字列またはPathオブジェクト）
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d', '%Y%m%d_%H%M%S'）

    Returns:
        Optional[datetime]: 抽出された日付。抽出できない場合はNone

    Raises:
        ValueError: 無効なフォーマット指定子が含まれている場合
    """
    try:
        path = Path(file_path) if isinstance(file_path, str) else file_path
        filename = path.stem

        # パターンとマッピングを構築
        pattern, mapping = _build_pattern_and_mapping(date_format)
        if not mapping:
            raise ValueError(
                f"有効な日付フォーマット指定子が含まれていません: {date_format}"
            )

        # ファイル名から日付部分を検索
        match = re.search(pattern, filename)
        if not match:
            return None

        # マッチした部分から日付文字列を再構成
        date_str = date_format
        for fmt, group_name in mapping.items():
            if group_name in match.groupdict():
                date_str = date_str.replace(fmt, match.group(group_name))

        # 日付文字列をdatetimeオブジェクトに変換
        try:
            dt = datetime.strptime(date_str, date_format)
            # 日付の妥当性を追加チェック（strptimeは2月31日などを3月3日として受け入れてしまう）
            if dt.month != int(match.group("month")) or dt.day != int(
                match.group("day")
            ):
                return None
            return dt
        except (ValueError, KeyError):
            return None

    except ValueError as e:
        if "有効な日付フォーマット指定子" in str(e):
            raise
        return None
    except Exception:
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
    date_format: Union[str, List[str]],
    deadline: Union[datetime, timedelta, int],
    recursive: bool = False,
    file_filter: Optional[List[str]] = None,
) -> int:
    """
    ファイル名の日付を基準に、指定されたディレクトリ内の期限切れファイルをすべて削除します

    Args:
        dir_path: 削除対象ディレクトリのパス
        date_format: 日付フォーマット（例: '%Y%m%d', '%Y-%m-%d'）またはフォーマットのリスト
        deadline: 期限を示すデータ
            - datetime型: この日時より前の日付を持つファイルは期限切れと判定
            - timedelta型: 現在時刻からこの時間差より前の日付を持つファイルは期限切れと判定
            - int型: 現在日からこの日数より前の日付を持つファイルは期限切れと判定
        recursive: サブディレクトリも対象とするかどうか (デフォルト: False)
        file_filter: 対象とするファイル拡張子のリスト (例: ['.txt', '.log'])

    Returns:
        int: 削除されたファイルの数

    Raises:
        FileNotFoundError: 指定されたディレクトリが存在しない場合
        NotADirectoryError: 指定されたパスがディレクトリではない場合
        PermissionError: ファイルの削除権限がない場合
    """
    path = Path(dir_path) if isinstance(dir_path, str) else dir_path

    if not path.exists():
        raise FileNotFoundError(f"ディレクトリが存在しません: {path}")

    if not path.is_dir():
        raise NotADirectoryError(f"指定されたパスはディレクトリではありません: {path}")

    # date_formatを常にリストとして扱う
    formats = [date_format] if isinstance(date_format, str) else date_format

    deleted_count = 0
    glob_pattern = "**/*" if recursive else "*"

    # ディレクトリ内のファイルを処理
    for item in path.glob(glob_pattern):
        # ディレクトリはスキップ
        if item.is_dir():
            continue

        # file_filterによるフィルタリング
        if file_filter is not None:
            if item.suffix and any(ext == item.suffix for ext in file_filter):
                pass
            else:
                continue

        # 削除可能かどうかをチェック
        if not os.access(item, os.W_OK):
            raise PermissionError(f"ファイル {item} の削除権限がありません")

        try:
            # いずれかのフォーマットで期限切れと判定されたら削除
            for fmt in formats:
                if is_filename_date_expired(item, fmt, deadline):
                    try:
                        item.unlink()
                        deleted_count += 1
                        break
                    except PermissionError as e:
                        raise PermissionError(
                            f"ファイル {item} の削除権限がありません: {e}"
                        )
                    except OSError as e:
                        print(f"ファイル {item} の削除に失敗しました: {e}")
                        break

        except (PermissionError, OSError) as e:
            raise PermissionError(f"ファイル {item} の削除に失敗しました: {e}")

    return deleted_count
