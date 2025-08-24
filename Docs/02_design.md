# Chat App - 設計書

## 1. 技術スタック
- **バックエンド**: Flask, Flask-SocketIO, eventlet
- **データベース**: SQLite
- **フロントエンド**: HTML, CSS, JavaScript (Socket.IO client)

## 2. データベース設計
### `messages` テーブル
| フィールド名 | データ型 | 説明 |
| :--- | :--- | :--- |
| `id` | INTEGER | 主キー（自動採番） |
| `room` | TEXT | ルーム名 |
| `username` | TEXT | ユーザー名 |
| `message` | TEXT | メッセージ内容 |
| `timestamp`| TEXT | 送信日時 (形式: 'YYYY-MM-DD HH:MM:SS') |

## 3. URL設計（ルーティング）
| URL | HTTPメソッド | 機能 | Blueprint |
| :--- | :--- | :--- | :--- |
| `/chat/` | GET | ログインページ表示 | `chat.index` |
| `/chat/chat` | GET | チャットルーム表示 | `chat.chat` |

## 4. リアルタイム通信設計 (Socket.IO Events)
| イベント名 | 送信者 | 受信者 | 内容 |
| :--- | :--- | :--- | :--- |
| `join` | クライアント | サーバー | ルーム参加を通知 |
| `text` | クライアント | サーバー | 新規メッセージを送信 |
| `status` | サーバー | 特定ルーム | ユーザーの入退室を通知 |
| `message`| サーバー | 特定ルーム | 新規メッセージを配信 |