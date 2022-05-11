@alguien, shared an amazing CTF challenge. I tried to figure it out and learned a lot along the way. I had to wait until he showed how to solve 
it because I couldn't do it.

The challenge is up on http://challenge.alguien.site:31337/
There is a simple login form where we can try to log in with different default credentials.

One of the first attemps is to try SQL injections, like `admin' or '1'='1` but it throws an error.
![screenshot]()

Now, let's take a look into the page source code, this is always the first step in every web app hacking.
Here, we can find a clue.
