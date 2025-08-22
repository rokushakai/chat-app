import sqlite3
import datetime
import csv
from io import StringIO
import re
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
from jinja2 import pass_eval_context as evalcontextfilter
from markupsafe import Markup, escape

app = Flask(__name__)
app.secret_key = 'your_chat_secret_key'
socketio = SocketIO(app, path='/socket.io')
DATABASE = 'chat.db'

@app.template_filter('nl2br')
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in re.split(r'(?:\r\n|\r|\n){2,}', escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if not username or not room:
        return redirect(url_for('index'))
    
    db = get_db()
    messages = db.execute(
        'SELECT * FROM messages WHERE room = ? ORDER BY timestamp ASC', (room,)
    ).fetchall()
    db.close()
    
    return render_template('chat.html', username=username, room=room, messages=messages)

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': f"{username} が入室しました。"}, to=room)

@socketio.on('text')
def on_text(data):
    username = data['username']
    room = data['room']
    msg = data['msg']
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    db = get_db()
    db.execute(
        'INSERT INTO messages (room, username, message, timestamp) VALUES (?, ?, ?, ?)',
        (room, username, msg, timestamp)
    )
    db.commit()
    db.close()

    emit('message', {'username': username, 'msg': msg, 'timestamp': timestamp}, to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': f"{username} が退出しました。"}, to=room)

@app.route('/search')
def search():
    username = request.args.get('username')
    room = request.args.get('room')
    keyword = request.args.get('keyword', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    db = get_db()
    query = 'SELECT * FROM messages WHERE room = ?'
    params = [room]

    if keyword:
        query += ' AND message LIKE ?'
        params.append(f'%{keyword}%')
    if start_date:
        query += ' AND timestamp >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND timestamp <= ?'
        params.append(f'{end_date} 23:59:59')
    
    query += ' ORDER BY timestamp DESC'
    results = db.execute(query, tuple(params)).fetchall()
    db.close()

    return render_template('search_results.html', results=results, username=username, room=room)

@app.route('/export_csv')
def export_csv():
    room = request.args.get('room')
    db = get_db()
    messages = db.execute(
        'SELECT * FROM messages WHERE room = ? ORDER BY timestamp ASC', (room,)
    ).fetchall()
    db.close()

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['日時', 'ユーザー名', 'メッセージ'])
    for msg in messages:
        cw.writerow([msg['timestamp'], msg['username'], msg['message']])
    
    output = si.getvalue()
    
    # ファイル名をURLエンコードして日本語に対応
    filename = quote(f"chat_log_{room}.csv")
    
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename*=UTF-8''{filename}"})

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Initialized the database.')

if __name__ == '__main__':
    socketio.run(app, debug=True)