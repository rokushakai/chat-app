\# リアルタイム・マルチチャットアプリケーション



\## 概要

FlaskとWebSocket技術（Flask-SocketIO）を使って構築した、リアルタイムで複数人・複数ルームでの会話が可能なチャットアプリケーションです。会話履歴はサーバー上に保存され、高度な検索機能も備えています。



このプロジェクトは、Webアプリケーション開発とデプロイの基礎スキルを習得するために作成されました。



---



\## ✨ 機能一覧

\- \*\*ロビー機能:\*\* アプリケーションの入口で、ユーザー名と参加したいルーム名を入力できます。

\- \*\*マルチチャットルーム:\*\*

&nbsp;   - 任意の名前でルームを作成し、参加できます。

&nbsp;   - ルーム内の会話は、他のルームからは見えないように完全に分離されています。

\- \*\*リアルタイムメッセージング:\*\*

&nbsp;   - WebSocketを利用し、ページをリロードすることなくメッセージが即座に全参加者に配信されます。

&nbsp;   - 他のユーザーが入室した際のステータスメッセージも表示されます。

\- \*\*タイムスタンプ:\*\* 全てのメッセージに、サーバーで記録された送信日時が表示されます。

\- \*\*会話履歴の永続化:\*\*

&nbsp;   - ルームごとの会話履歴が、サーバー上に個別のCSVファイルとして自動で保存されます。

\- \*\*高度な履歴検索:\*\*

&nbsp;   - メッセージ本文に含まれるキーワードでのフリーワード検索が可能です。

&nbsp;   - 日付（開始日・終了日）を指定した期間での絞り込み検索が可能です。

&nbsp;   - 上記の複合検索にも対応しています。



---



\## 🛠️ 使用技術

\- \*\*バックエンド:\*\*

&nbsp;   - Python 3.9+

&nbsp;   - Flask

&nbsp;   - Flask-SocketIO

&nbsp;   - Gunicorn (WSGI Server)

&nbsp;   - eventlet (非同期ワーカー)

\- \*\*フロントエンド:\*\*

&nbsp;   - HTML

&nbsp;   - CSS

&nbsp;   - JavaScript (Socket.IO Client)

\- \*\*インフラ・デプロイ:\*\*

&nbsp;   - AWS EC2 (Amazon Linux 2023)

&nbsp;   - Nginx

&nbsp;   - systemd



---



\## 🚀 セットアップとローカルでの実行方法



1\.  \*\*リポジトリをクローン\*\*

&nbsp;   ```sh

&nbsp;   git clone \[https://github.com/あなたのユーザー名/あなたのリポジトリ名.git](https://github.com/あなたのユーザー名/あなたのリポジトリ名.git)

&nbsp;   cd chat-app

&nbsp;   ```

2\.  \*\*仮想環境の作成と有効化\*\*

&nbsp;   ```sh

&nbsp;   # Windowsの場合

&nbsp;   python -m venv venv

&nbsp;   venv\\Scripts\\activate



&nbsp;   # Linux/macOSの場合

&nbsp;   python3 -m venv venv

&nbsp;   source venv/bin/activate

&nbsp;   ```

3\.  \*\*必要なライブラリをインストール\*\*

&nbsp;   ```sh

&nbsp;   pip install -r requirements.txt

&nbsp;   ```

4\.  \*\*開発サーバーを起動\*\*

&nbsp;   ```sh

&nbsp;   python app.py

&nbsp;   ```

5\.  \*\*ブラウザでアクセス\*\*

&nbsp;   ブラウザで `http://127.0.0.1:5000` を開きます。

