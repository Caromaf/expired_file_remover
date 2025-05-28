#!/usr/bin/env python
"""
expired-file-removerの使用サンプル
"""
import argparse
import sys
from pathlib import Path

from expired_file_remover import remove_expired_files


def parse_args():
    """コマンドライン引数をパースします"""
    parser = argparse.ArgumentParser(
        description="指定したディレクトリ内の古いファイルを削除します"
    )
    parser.add_argument("directory", type=str, help="削除対象のディレクトリパス")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="この日数より古いファイルを削除（デフォルト: 30）",
    )
    parser.add_argument(
        "--recursive", action="store_true", help="サブディレクトリも対象にする"
    )
    parser.add_argument(
        "--extensions",
        type=str,
        nargs="+",
        help="対象とするファイル拡張子（例: .txt .log）",
    )
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_args()

    dir_path = Path(args.directory)

    # ディレクトリの存在確認
    if not dir_path.exists():
        print(f"エラー: ディレクトリ {dir_path} が見つかりません", file=sys.stderr)
        sys.exit(1)

    if not dir_path.is_dir():
        print(f"エラー: {dir_path} はディレクトリではありません", file=sys.stderr)
        sys.exit(1)

    print(f"ディレクトリ: {dir_path}")
    print(f"期限: {args.days}日より古いファイル")
    if args.recursive:
        print("再帰的に処理: はい")
    else:
        print("再帰的に処理: いいえ")

    if args.extensions:
        print(f"対象拡張子: {', '.join(args.extensions)}")
        # 拡張子の先頭にドットがない場合は追加
        file_filter = [
            ext if ext.startswith(".") else f".{ext}" for ext in args.extensions
        ]
    else:
        print("対象拡張子: すべて")
        file_filter = None

    # 処理を実行
    try:
        count = remove_expired_files(
            dir_path, args.days, recursive=args.recursive, file_filter=file_filter
        )
        print(f"\n削除されたファイル数: {count}")
    except Exception as e:
        print(f"エラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
