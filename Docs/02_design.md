\# 1. 使用技術

\- \*\*バックエンド:\*\* Flask, Python

\- \*\*リアルタイム通信:\*\* Flask-SocketIO

\- \*\*WSGIサーバー:\*\* Gunicorn

\- \*\*非同期ワーカー:\*\* eventlet

\- \*\*Webサーバー:\*\* Nginx

\- \*\*フロントエンド:\*\* HTML, CSS, JavaScript (Socket.IO Client)

\- \*\*Python標準ライブラリ:\*\* datetime, csv, os



\# 2. アーキテクチャ概要

1\. ユーザーはルート(`/`)にアクセスし、ロビーページ(`lobby.html`)を表示する。

2\. フォームに名前とルーム名を入力して送信すると、`/chat?username=...\&room=...`というURLに遷移する。

3\. `/chat`ページ(`index.html`)のJavaScriptが、URLパラメータを読み取り、サーバーとのWebSocket接続を確立する。

4\. 接続後、クライアントは`join`イベントをサーバーに送信する。

5\. サーバーは`join`イベントを受け取り、クライアントを特定のルームに参加させ、入室通知をそのルームに配信する。

6\. ユーザーがメッセージを送信すると、クライアントは`send\_message`イベントをサーバーに送信する。

7\. サーバーはメッセージにタイムスタンプを付与し、ルーム別のCSVファイルに追記保存した後、同じルームの全クライアントに`broadcast\_message`イベントでメッセージを配信する。

8\. ユーザーが履歴を検索すると、クライアントは`search\_history`イベントをサーバーに送信する。

9\. サーバーは対応するCSVファイルを読み込み、検索条件でフィルタリングした後、`load\_history`イベントで結果を要求元のクライアントにのみ返信する。



\# 3. イベント設計

\- \*\*クライアント → サーバー:\*\*

&nbsp;   - `join`: ユーザーが特定のルームに参加する。

&nbsp;       - データ: `{'username': 'ユーザー名', 'room': 'ルーム名'}`

&nbsp;   - `send\_message`: ユーザーが新しいメッセージを送信する。

&nbsp;       - データ: `{'username': 'ユーザー名', 'message': 'メッセージ本文', 'room': 'ルーム名'}`

&nbsp;   - `search\_history`: ユーザーが履歴検索を要求する。

&nbsp;       - データ: `{'room': 'ルーム名', 'keyword': '検索語', 'start\_date': '日付', 'end\_date': '日付'}`

\- \*\*サーバー → クライアント:\*\*

&nbsp;   - `status`: ユーザーの入退室などを通知する。

&nbsp;       - データ: `{'msg': 'ステータスメッセージ'}`

&nbsp;   - `broadcast\_message`: サーバーがチャットメッセージを配信する。

&nbsp;       - データ: `{'username': 'ユーザー名', 'message': 'メッセージ本文', 'timestamp': '日時'}`

&nbsp;   - `load\_history`: サーバーが検索結果の履歴を送信する。

&nbsp;       - データ: `\[{'username': '...', 'message': '...', 'timestamp': '...'}, ...]` (メッセージオブジェクトの配列)



\# 4. データ保存設計

メッセージ履歴は、サーバーのファイルシステム上に、ルームごとのCSVファイルとして保存する。

\- \*\*ファイル名:\*\* `history\_` + `ルーム名` + `.csv` (例: `history\_music.csv`)

\- \*\*フォーマット:\*\* UTF-8

\- \*\*カラム:\*\* `timestamp`, `username`, `message`



\# 5. ディレクトリ構成

\- `chat-app/`

&nbsp;   - `app.py`

&nbsp;   - `templates/`

&nbsp;       - `lobby.html`

&nbsp;       - `index.html`

&nbsp;   - `venv/`

&nbsp;   - `requirements.txt`

&nbsp;   - `history\_\*.csv` (実行時に自動生成)

&nbsp;   - `Docs/`

