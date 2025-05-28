"""
pytestの設定ファイル
テスト実行時のパス設定などを行う
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
# これにより、テストコードから直接 'expired_file_remover' をインポートできる
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
