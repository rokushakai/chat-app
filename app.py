import sqlite3
import datetime
import re
import csv
from io import StringIO
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, Blueprint, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
from jinja2 import pass_eval_context as evalcontextfilter
from markupsafe import Markup, escape

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')
socketio = SocketIO()
DATABASE = 'chat.db'

@chat_bp.app_template_filter('nl2br')
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

def close_connection(exception):
    pass

@chat_bp.route('/')
def index():
    return render_template('login.html')

@chat_bp.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if not username or not room:
        return redirect(url_for('chat.index'))
    db = get_db()
    messages = db.execute('SELECT * FROM messages WHERE room = ? ORDER BY timestamp ASC', (room,)).fetchall()
    db.close()
    return render_template('chat.html', username=username, room=room, messages=messages)

@socketio.on('join')
def on_join(data):
    username = data['username']; room = data['room']
    join_room(room); emit('status', {'msg': f"{username} が入室しました。"}, to=room)

@socketio.on('text')
def on_text(data):
    username = data['username']; room = data['room']; msg = data['msg']
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db = get_db()
    db.execute('INSERT INTO messages (room, username, message, timestamp) VALUES (?, ?, ?, ?)',(room, username, msg, timestamp))
    db.commit(); db.close()
    emit('message', {'username': username, 'msg': msg, 'timestamp': timestamp}, to=room)

# ▼▼▼ ここから下の関数を追加 ▼▼▼

def build_chat_search_query_and_params():
    """チャット履歴検索クエリを構築する"""
    query = 'SELECT * FROM messages WHERE room = :room'
    params = {'room': request.args.get('room')}

    if request.args.get('keyword'):
        query += ' AND message LIKE :keyword'
        params['keyword'] = f"%{request.args.get('keyword')}%"
    if request.args.get('start_date'):
        query += ' AND date(timestamp) >= :start_date'
        params['start_date'] = request.args.get('start_date')
    if request.args.get('end_date'):
        query += ' AND date(timestamp) <= :end_date'
        params['end_date'] = request.args.get('end_date')
    
    query += ' ORDER BY timestamp DESC'
    return query, params

@chat_bp.route('/search')
def search():
    """チャット履歴の検索結果を表示する"""
    query, params = build_chat_search_query_and_params()
    db = get_db()
    results = db.execute(query, params).fetchall()
    db.close()
    return render_template('search_results.html', results=results, room=request.args.get('room'), username=request.args.get('username'))

@chat_bp.route('/export_csv')
def export_csv():
    """チャット履歴をCSVとしてエクスポートする"""
    query, params = build_chat_search_query_and_params()
    db = get_db()
    results = db.execute(query, params).fetchall()
    db.close()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['日時', 'ユーザー名', 'メッセージ'])
    for msg in results:
        cw.writerow([msg['timestamp'], msg['username'], msg['message']])
    
    output = si.getvalue()
    filename = quote(f"chat_log_{request.args.get('room')}.csv")
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename*=UTF-8''{filename}"})

# ▲▲▲ ここまで追加 ▲▲▲

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your_chat_secret_key'
    app.teardown_appcontext(close_connection)
    app.register_blueprint(chat_bp)
    socketio.init_app(app, path='/socket.io')
    return app

app = create_app()

@app.cli.command('init-db')
def init_db_command():
    from . import init_db # init_db関数を正しくインポート
    init_db()
    print('Initialized the database.')