"""
expired_file_remover - 期限切れファイルを削除するパッケージ
"""

from .core import is_expired, remove_expired_file, remove_expired_files

__all__ = ["remove_expired_file", "remove_expired_files", "is_expired"]
