"""
エクスパイア（有効期限切れ）したファイルを削除するモジュール
"""

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
