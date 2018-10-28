from flask import Flask, json, request, url_for, redirect, abort
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_socketio import SocketIO
import uuid
import datahelper
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'secret')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
socket = SocketIO(app)

active_users = {}

class User(UserMixin):
    def __init__(self):
        self.name = "Steve"
        self.id = str(uuid.uuid4())
        self.chat_id = None

def leave_chat(user):
    chatroom = get_chatroom_by_id(user.chat_id)
    user.chat_id = None
    chatroom.users.remove(user)

def send_message(user, msg):
    data = {'name' : user.name,
            'msg'  : msg }
    socket.emit(f'chatroom_{user.chat_id}', data, broadcast=True)

@login_manager.user_loader
def load_user(id):
    return active_users.get(id)
        
@app.route('/')
def homepage():
    return "homepage things"

@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        chatrooms = [{'name':'General Discussion', 'users': ['1']}, {'name':'Battling Leukemia', 'users': ['1','2','3']}, {'name':'Support', 'users': ['1','2','3']},{'name':'memers', 'users': ['1','2']},{'name':'memers', 'users': ['1','2','3']},{'name':'memers', 'users': ['1']}]
        return render_template('all_chat.html', chatrooms=chatrooms)
        #return render_template('login.html')
    else:
        username = "safe"
        password = "env"
        if datahelper.auth(username, password):
            login_user(User())
            return redirect(url_for("db"))
        else:
            return redirect(url_for("login"))

@app.route('/db')
@login_required
def db():
    return "good boi, logged in"

@app.route('/kb')
def kb():
    return "wiki"

@app.route('/profile')
@login_required
def profile():
    return "profile"

@app.route('/logout')
@login_required
def logout():
    leave_chat(current_user)
    logout_user()
    return redirect(url_for('homepage'))

@app.route('/allchat')
@login_required
def all_chat():
    chatrooms = get_free_chatrooms(get_chatrooms())
    return "chatrooms"

@app.route('/chat/<int:chatyppl>')
@login_required
def chat(id):
    chatroom = get_chatroom_by_id(id)
    chatroom.users.append(current_user)
    current_user.chat_id = id
    return f'In chat {id}'

@app.route('/chat/<int:chatyppl>/post', methods = ['POST'])
@login_required
def post_chat(id):
    chatroom = get_chatroom_by_id(id)
    message = request.data
    chatroom.messages.append(message)
    send_message(current_user, message)

@app.route('/buddy')
@login_required
def buddy():
    return "ppl i liked"

@app.route('/forum')
@login_required
def forum():
    return "this is a forum, sorry i couldn't think of something funny"

if __name__ == "__main__":
    app.run()
