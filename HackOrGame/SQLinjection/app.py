from flask import Flask, render_template, request
import sqlite3
import os


FLAG = os.getenv('FLAG') or 'FLAG{dummy_flag}'
app = Flask(__name__)


def check_login(username, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        res = cur.execute(f"select 1,'admin','123456','{FLAG}' from users where username='{username}'").fetchone()
    except:
        return False
    finally:
        cur.close()
        con.close()
    if res is None:
        return False
    if password == res[2]:
        return True
    return False


@app.route('/', methods=['GET', 'DEBUG'])
def index():
    if request.method == 'DEBUG':
        return open(__file__, 'rt').read()
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if check_login(username, password):
        return render_template('index.html', success='Nice, you are logged in! But... Where is the flag?')
    return render_template('index.html', error='Sorry, your username or password is bad')


def create_database():
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('create table users (id integer primary key, username varchar(100), password varchar(100), flag varchar(100))')
    cur.execute("insert into users values (1, 'admin', '123456', '')")
    con.commit()
    cur.close()
    con.close()


if __name__ == '__main__':
    # create_database()     # the database already exists
    app.run(debug=True)
