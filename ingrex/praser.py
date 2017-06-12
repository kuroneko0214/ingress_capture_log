"Ingrex praser deal with message"
from datetime import datetime, timedelta


class Message(object):
    "Message object"

    def __init__(self, raw_msg):
        self.raw = str(raw_msg).replace("'", "")
        self.guid = raw_msg[0]
        self.timestamp = raw_msg[1]
        seconds, millis = divmod(raw_msg[1], 1000)
        time = datetime.utcfromtimestamp(seconds) + timedelta(milliseconds=millis) + timedelta(hours=8)
        self.time = time.strftime('%Y-%m-%d %H:%M:%S')
        self.text = raw_msg[2]['plext']['text']
        self.team = raw_msg[2]['plext']['team']
        self.type = raw_msg[2]['plext']['plextType']
        if self.type == "SYSTEM_BROADCAST":
            try:
                self.player_info = raw_msg[2]['plext']['markup'][0]
                self.player_team = self.player_info[1]['team']
                self.player_name = self.player_info[1]['plain']
                self.player_action = raw_msg[2]['plext']['markup'][1][1]['plain']
                self.portal_info = raw_msg[2]['plext']['markup'][2]
                self.portal_name = self.portal_info[1]['name'].replace("'", "")
                self.portal_addr = self.portal_info[1]['address'].replace("'", "")
                self.portal_lngE6 = self.portal_info[1]['lngE6']
                self.portal_latE6 = self.portal_info[1]['latE6']
                self.portal_text = self.portal_info[1]['plain'].replace("'", "")
                if self.portal_name is None:
                    self.portal_name = '[Unnamed Portal]'
            except Exception as e:
                print("Error! Please find raw data:", self.raw)
                raise e
        else:
            self.player_action = "posts"


class Portal(object):
    "Portal object"

    def __init__(self, raw_msg, fromdetail=False):
        self.raw = str(raw_msg).replace("'", "")
        try:
            if fromdetail:
                self.id = raw_msg[13]
                self.team = raw_msg[1]
                self.latE6 = raw_msg[2]
                self.lngE6 = raw_msg[3]
                self.name = raw_msg[8]
                self.owner = raw_msg[16]
            else:
                self.guid = raw_msg[0]
                self.id = raw_msg[1]
                self.team = raw_msg[2][1]
                self.latE6 = raw_msg[2][2]
                self.lngE6 = raw_msg[2][3]
                self.name = raw_msg[2][8]
            if self.name is None:
                self.name = '[Unnamed Portal]'
            else:
                self.name = self.name.replace("'", "")
        except Exception as e:
                print("Error! Please find raw data:", self.raw)
                raise e
