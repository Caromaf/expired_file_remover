# #!/bin/bash

# # .ssh ディレクトリのパーミッションを700にする
# # マウントされているディレクトリの場合、ホストのパーミッションが優先されますが、
# # 念のため実行しておきます
# sudo chmod 700 /home/vscode/.ssh

# # known_hosts ファイルが存在しない場合は作成し、パーミッションと所有者を設定
# # touch が失敗しても処理を続行するために || true を残します
# sudo touch /home/vscode/.ssh/known_hosts || true
# sudo chmod 600 /home/vscode/.ssh/known_hosts
# sudo chown vscode:vscode /home/vscode/.ssh/known_hosts

# # config ファイルや config.secret はマウントされたものなので、chmod は通常不要ですが、
# # 念のためパーミッションを正しく設定しようと試みる (dangling symlinkエラーは出なくなるはず)
# # chmod が失敗しても処理を続行するために || true をつけます
# sudo chmod 600 /home/vscode/.ssh/config || true
# sudo chmod 600 /home/vscode/.ssh/config.secret || true

# echo "SSH setup script finished."
