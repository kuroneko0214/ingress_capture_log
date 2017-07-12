from xml.etree import ElementTree as ET


class xmlReader(object):
    def __init__(self):
        self.tree = ET.parse('./ingrex_lib/data.xml')

    def getdbinfo(self):
        dbinfo = {}
        dbinfoE = self.tree.findall('./database/')
        for i in dbinfoE:
            dbinfo[i.tag] = i.text
        return dbinfo

    def getfieldrange(self):
        fieldrange = {}
        fieldrangeE = self.tree.findall('./field/')
        for i in fieldrangeE:
            fieldrange[i.tag] = int(i.text)
        return fieldrange

    def gettimedelta(self):
        timedelta = self.tree.find('./time/timedelta').text
        return int(timedelta)

    def getactions(self):
        actions = []
        actionsE = self.tree.findall('./actions/')
        for i in actionsE:
            actions.append(i.text)
        return actions

    def getcookiepath(self, islocal=False):
        if islocal:
            cookiepath = 'cookies'
        else:
            cookiepath = self.tree.find('./cookiepath').text
        return cookiepath

    def getquery(self, name):
        query = self.tree.find("./queries/query[@name='{}']".format(name)).text.strip()
        return query

    def getentityendings(self):
        entityendings = []
        entityendingsE = self.tree.findall('./entityendings/')
        for i in entityendingsE:
            entityendings.append(i.text)
        return entityendings

    def gettilekeyformat(self):
        tilekeyformat = self.tree.find('./tilekeyformat').text
        return tilekeyformat

    def getgoogleaccount(self):
        googleaccount = {}
        googleaccountE = self.tree.findall('./googleaccount/')
        for i in googleaccountE:
            googleaccount[i.tag] = i.text
        return googleaccount


if __name__ == '__main__':
    x = xmlReader()
    print(x.getdbinfo())
    print(x.getfieldrange())
    print(x.gettimedelta())
    print(x.getactions())
    print(x.getcookiepath())
    print(x.getquery("get_portal_gt7"))
    print(x.getentityendings())
    print(x.gettilekeyformat())
    print(x.getgoogleaccount())
