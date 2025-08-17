import os
import csv
from datetime import datetime
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# --- 通常のHTTPルーティング ---
@app.route('/')
def index():
    return render_template('lobby.html')

@app.route('/chat')
def chat():
    return render_template('index.html')

# --- WebSocketイベントハンドラ ---
@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(f'{username} がルーム {room} に参加しました')
    emit('status', {'msg': f'{username} が入室しました。'}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    
    # 1. タイムスタンプを作成
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['timestamp'] = timestamp
    
    # 2. CSVファイルに履歴を保存
    filename = f"history_{room}.csv"
    # ファイルがなければヘッダーを書き込む
    file_exists = os.path.exists(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'username', 'message']) # ヘッダー
        writer.writerow([timestamp, data['username'], data['message']])
        
    print(f"ルーム {room} へのメッセージ: {data}")
    # 3. 全員にメッセージをブロードキャスト（タイムスタンプ付き）
    emit('broadcast_message', data, room=room)

# 4. 新しいイベント：履歴検索
@socketio.on('search_history')
def handle_search_history(data):
    room = data['room']
    keyword = data.get('keyword', '').lower()
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    filename = f"history_{room}.csv"
    if not os.path.exists(filename):
        return # 履歴ファイルがなければ何もしない

    results = []
    with open(filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader) # ヘッダーをスキップ
        for row in reader:
            row_timestamp_str, row_username, row_message = row
            
            # キーワードフィルター
            if keyword and keyword not in row_message.lower():
                continue

            # 期間フィルター
            row_date = datetime.strptime(row_timestamp_str, '%Y-%m-%d %H:%M:%S').date()
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                if row_date < start_date:
                    continue
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if row_date > end_date:
                    continue
            
            results.append({
                'timestamp': row_timestamp_str,
                'username': row_username,
                'message': row_message
            })

    # 検索結果をリクエスト元のクライアントにだけ送信
    emit('load_history', results, room=request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    print('クライアントが切断しました')

if __name__ == '__main__':
    socketio.run(app, debug=True)