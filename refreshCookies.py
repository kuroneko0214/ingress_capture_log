import requests, re, time, json
import lxml
from bs4 import BeautifulSoup as bs
from requests.utils import cookiejar_from_dict
from datetime import datetime, timedelta
from ingrex.xmlReader import xmlReader


islocal = False
d = xmlReader()
tdelta = d.gettimedelta()
cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=tdelta)
print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start verify cookie status.')

with open(d.getcookiepath(islocal=islocal)) as cookie:
    cookie = cookie.read().strip()
print('Before refresh:')
print(cookie)
cookie_dict = {}
googleaccount = d.getgoogleaccount()
username, password = googleaccount['username'], googleaccount['password']

lst_keys = []
lst_values = []
lst_cookies = cookie.split(";")
for lst_cookie in lst_cookies:
    lst_keys.append(lst_cookie.split("=")[0].strip())
    lst_values.append(lst_cookie.split("=")[1].strip())
cookie_dict = dict(zip(lst_keys, lst_values))
cookie_dict.pop('SACSID')

try:
    s = requests.Session()
    s.cookies.update(cookie_dict)
    test = s.get('https://www.ingress.com/intel')
    r = s
    v = re.findall('/jsc/gen_dashboard_([\d\w]+).js"', test.text)[0]
    print(r.headers)
    print(v)
    print('cookies success')
except IndexError:
    print('Login and get new cookie.')
    _ = r.get('https://www.ingress.com/intel')
    time.sleep(5)
    login_url = re.findall('"(https://www\.google\.com/accounts/ServiceLogin.+?)"', _.text)[0]
    _ = r.get(login_url)
    time.sleep(5)
    username_xhr_url = 'https://accounts.google.com/accountLoginInfoXhr'
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://accounts.google.com',
        'referer': 'https://accounts.google.com/ServiceLogin?service=ah&passive=true&continue=https%3A%2F%2Fappengine.google.com%2F_ah%2Fconflogin%3Fcontinue%3Dhttps%3A%2F%2Fwww.ingress.com%2Fintel&ltmpl=gm&shdf=ChMLEgZhaG5hbWUaB0luZ3Jlc3MMEgJhaCIUDxXHTvPWkR39qgc9Ntp6RlMnsagoATIUG3HUffbxSU31LjICBdNoinuaikg',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    }
    html = bs(_.text, 'lxml')

    data = {
        'Email': username,
    }
    for i in html.form.select('input'):
        try:
            if i['name'] == 'Page':
                data.update({'Page': i['value']})
            elif i['name'] == 'service':
                data.update({'service': i['value']})
            elif i['name'] == 'ltmpl':
                data.update({'ltmpl': i['value']})
            elif i['name'] == 'continue':
                data.update({'continue': i['value']})
            elif i['name'] == 'gxf':
                data.update({'gxf': i['value']})
            elif i['name'] == 'GALX':
                data.update({'GALX': i['value']})
            elif i['name'] == 'shdf':
                data.update({'shdf': i['value']})
            elif i['name'] == '_utf8':
                data.update({'_utf8': i['value']})
            elif i['name'] == 'bgresponse':
                data.update({'bgresponse': i['value']})
            else:
                pass
        except KeyError:
            pass
    _ = r.post(username_xhr_url, data=data, headers=headers)
    time.sleep(5)
    password_url = 'https://accounts.google.com/signin/challenge/sl/password'
    data.update({'Page': 'PasswordSeparationSignIn'})
    data.update({'identifiertoken': ''})
    data.update({'identifiertoken_audio': ''})
    data.update({'identifier-captcha-input': ''})
    data.update({'Passwd': password})
    data.update({'PersistentCookie': 'yes'})
    _ = r.post(password_url, headers=headers, data=data, allow_redirects=True)
    time.sleep(5)
    _ = r.get('https://www.ingress.com/intel')
    time.sleep(5)
    try:
        v = re.findall('/jsc/gen_dashboard_([\d\w]+).js"', _.text)[0]
    except Exception as e:
        print(_.text)
        print(_.request.headers)
        raise e
    print(v)
    cookiestr = _.request.headers['Cookie']
    print('After refresh:')
    print(cookiestr)
    file = open(d.getcookiepath(islocal=islocal), 'w')
    file.write(cookiestr)
    file.close()

print('-' * 80)
