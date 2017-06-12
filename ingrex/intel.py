"Ingrex is a python lib for ingress"
# import requests
import re
import json
import time


class Intel(object):
    "main class with all Intel functions"

    def __init__(self, cookies, field, session):

        self.session = session
        self.cookies = cookies
        self.token = re.findall(r'csrftoken=(\w*);', cookies)[0]
        self.headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'content-type': 'application/json; charset=UTF-8',
            'cookie': cookies,
            'origin': 'https://www.ingress.com',
            'referer': 'https://www.ingress.com/intel',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'x-csrftoken': self.token,
        }
        self.field = {
            'maxLatE6': field['maxLatE6'],
            'minLatE6': field['minLatE6'],
            'maxLngE6': field['maxLngE6'],
            'minLngE6': field['minLngE6'],
        }
        self.point = {
            'latE6': (field['maxLatE6'] + field['minLatE6']) >> 1,
            'lngE6': (field['maxLngE6'] + field['minLngE6']) >> 1,
        }
        self.refresh_version()

    def refresh_version(self):
        "refresh api version for request"

        lst_keys = []
        lst_values = []
        lst_cookies = self.cookies.split(";")
        for lst_cookie in lst_cookies:
            lst_keys.append(lst_cookie.split("=")[0].strip())
            lst_values.append(lst_cookie.split("=")[1].strip())
        cookies = dict(zip(lst_keys, lst_values))
        self.session.headers.update(self.headers)
        self.session.cookies.update(cookies)
        try:
            request = self.session.get('https://www.ingress.com/intel')
            self.version = re.findall(r'gen_dashboard_(\w*)\.js', request.text)[0]
        except Exception as e:
            print("Meet and exception. Please check whether cookie is expired...")
            print(self.session.cookies.items())
            print(request.text)
            raise e

    def fetch(self, url, payload):
        "raw request with auto-retry and connection check function"
        lst_keys = []
        lst_values = []
        lst_cookies = self.cookies.split(";")
        for lst_cookie in lst_cookies:
            lst_keys.append((lst_cookie.split("=")[0]).strip())
            lst_values.append((lst_cookie.split("=")[1]).strip())
        cookies = dict(zip(lst_keys, lst_values))
        self.session.headers.update(self.headers)
        self.session.cookies.update(cookies)
        # print(cookies)
        payload['v'] = self.version
        try:
            request = self.session.post(url, data=json.dumps(payload))
            result = request.json()['result']
        except Exception as e:
            print("Meet and exception. Please check whether cookie is expired...")
            print(self.session.cookies.items())
            print(request.text)
            raise e
        finally:
            # request.close()
            return result

    def fetch_msg(self, mints=-1, maxts=-1, reverse=False, tab='all'):
        "fetch message from Ingress COMM, tab can be 'all', 'faction', 'alerts'"
        url = 'https://www.ingress.com/r/getPlexts'
        payload = {
            'maxLatE6': self.field['maxLatE6'],
            'minLatE6': self.field['minLatE6'],
            'maxLngE6': self.field['maxLngE6'],
            'minLngE6': self.field['minLngE6'],
            'maxTimestampMs': maxts,
            'minTimestampMs': mints,
            'tab': tab
        }
        if reverse:
            payload['ascendingTimestampOrder'] = True
        return self.fetch(url, payload)

    def fetch_map(self, tilekeys):
        "fetch game entities from Ingress map"
        url = 'https://www.ingress.com/r/getEntities'
        payload = {
            'tileKeys': tilekeys
        }
        return self.fetch(url, payload)

    def fetch_portal(self, guid):
        "fetch portal details from Ingress"
        url = 'https://www.ingress.com/r/getPortalDetails'
        payload = {
            'guid': guid
        }
        return self.fetch(url, payload)

    def fetch_score(self):
        "fetch the global score of RESISTANCE and ENLIGHTENED"
        url = 'https://www.ingress.com/r/getGameScore'
        payload = {}
        return self.fetch(url, payload)

    def fetch_region(self):
        "fetch the region info of RESISTANCE and ENLIGHTENED"
        url = 'https://www.ingress.com/r/getRegionScoreDetails'
        payload = {
            'lngE6': self.point['lngE6'],
            'latE6': self.point['latE6'],
        }
        return self.fetch(url, payload)

    def fetch_artifacts(self):
        "fetch the artifacts details"
        url = 'https://www.ingress.com/r/getArtifactPortals'
        payload = {}
        return self.fetch(url, payload)

    def send_msg(self, msg, tab='all'):
        "send a message to Ingress COMM, tab can be 'all', 'faction'"
        url = 'https://www.ingress.com/r/sendPlext'
        payload = {
            'message': msg,
            'latE6': self.point['latE6'],
            'lngE6': self.point['lngE6'],
            'tab': tab
        }
        return self.fetch(url, payload)

    def send_invite(self, address):
        "send a recruit to an email address"
        url = 'https://www.ingress.com/r/sendInviteEmail'
        payload = {
            'inviteeEmailAddress': address
        }
        return self.fetch(url, payload)

    def redeem_code(self, passcode):
        "redeem a passcode"
        url = 'https://www.ingress.com/r/redeemReward'
        payload = {
            'passcode': passcode
        }
        return self.fetch(url, payload)


if __name__ == '__main__':
    pass
