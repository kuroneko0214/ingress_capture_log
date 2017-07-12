from ingrex import Intel, Utils
import ingrex, pymysql, time
import requests, sys
from datetime import datetime, timedelta
from ingrex.xmlReader import xmlReader


def main():
    "main function"
    islocal = True
    d = xmlReader()
    tdelta = d.gettimedelta()
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=tdelta)
    print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start insert portal list.')
    if islocal is False:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    field = d.getfieldrange()
    s = requests.Session()
    tilekeys = get_tile_keys()
    if len(tilekeys) > 0:
        for i in range(0, len(tilekeys)):
            if i >= 30:
                print('Tilekey list is too long. Only select 30 tilekeys to process...')
                break
            key = tilekeys[i]
            tilekey = key[0]
            print(tilekey)
            with open(d.getcookiepath(islocal=islocal)) as cookies:
                cookies = cookies.read().strip()
            intel = Intel(cookies, field, s)
            result = intel.fetch_map([tilekey])
            entities = result['map'][tilekey]['gameEntities']
            try:
                for entity in entities:
                    if entity[0][-3:] in d.getentityendings():
                        portal = ingrex.Portal(entity)
                        insert_portal_from_tile(portal)
            except Exception as e:
                update_tile_sync_status(tilekey, syncfail=True)
                print(e)
            else:
                update_tile_sync_status(tilekey)
            time.sleep(60)
    else:
        print('No tilekey to be fetched.')
    print('-' * 80)


def get_tile_keys():
    try:
        query_select = get_query(name="get_tile_keys")
        db, cursor = connect_to_db()
        c = cursor.execute(query_select)
        r = cursor.fetchall()
        print('Get {} tile key(s).'.format(c))
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)
    return r


def get_portal_in_tile(portal):
    try:
        query_tile = get_query(name="select_portal_in_tilekey").format(portal.lngE6, portal.latE6, portal.name)
        db, cursor = connect_to_db()
        c = cursor.execute(query_tile)
        r = ''
        if c == 1:
            r = cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)
    return r


def get_portal_in_capture(guid):
    try:
        query_select = get_query(name="select_portal_by_guid").format(guid)
        db, cursor = connect_to_db()
        c = cursor.execute(query_select)
        r = ''
        if c == 1:
            r = cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)
    return r


def update_capture_baseinfo(pcinfo, tileinfo, portal):
    try:
        query_update = get_query(name="update_portal_baseinfo")
        db, cursor = connect_to_db()
        addr = ''
        if tileinfo:
            addr = tileinfo[0][7]
        query_update = query_update.format(portal.id, portal.name, addr, portal.lngE6, portal.latE6, portal.guid)
        cursor.execute(query_update)
        db.commit()
        print('Portal[{}] base info is updated. Portal Name[{} --> {}]. Portal Addr[{} --> {}]. Lng, lat[{}, {} --> {}, {}]'\
            .format(portal.guid, pcinfo[0][4], portal.name, pcinfo[0][5], addr, pcinfo[0][6], pcinfo[0][7], portal.lngE6, portal.latE6))
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)


def insert_portal_from_tile(portal):
    try:
        query_insert = get_query(name="insert_capture_list")
        query_update = get_query(name="update_capture_time")
        query_pureupdate = get_query(name="update_update_time")
        db, cursor = connect_to_db()
        pcinfo = get_portal_in_capture(portal.guid)
        tileinfo = get_portal_in_tile(portal)
        ctime = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)
        ctime = ctime.strftime('%Y-%m-%d %H:%M:%S')

        if pcinfo:
            if (pcinfo[0][4] != portal.name) or (pcinfo[0][6] != str(portal.lngE6)) or (pcinfo[0][7] != str(portal.latE6)):
                update_capture_baseinfo(pcinfo, tileinfo, portal)
        query = ''
        ispureupdate = False
        if tileinfo and (tileinfo[0][5] == ' captured '):
            owner, team, ctime = tileinfo[0][4], tileinfo[0][3][0], tileinfo[0][1]
            if pcinfo:
                if (pcinfo[0][9] is None) or (pcinfo[0][9] == ''):
                    if team == 'N':
                        ctime = ''
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif team == 'N':
                    ctime = ''
                    owner = ''
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif (pcinfo[0][9] != team) or (pcinfo[0][8] != owner):
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif (pcinfo[0][9] == team) and (pcinfo[0][8] == owner):
                    query = query_pureupdate.format(portal.guid)
                    ispureupdate = True
                else:
                    print("Failed to sync data for portal[{}]".format(portal.guid))
                    return False
                if ispureupdate:
                    print("Portal[{}] is found. No action is required.".format(portal.guid))
                else:
                    print("Portal[{}] is updated. Owner[{} --> {}]. Team[{} --> {}]. Capture Time[{} --> {}]."\
                            .format(portal.guid, pcinfo[0][8], owner, pcinfo[0][9], team, pcinfo[0][10], ctime))
            else:
                query = query_insert.format(portal.guid, portal.id, tileinfo[0][6], tileinfo[0][7], tileinfo[0][8], tileinfo[0][9], owner, team, ctime, portal.raw)
                print("Portal[{}] is inserted.".format(portal.guid))
        else:
            owner, team = '', portal.team
            if pcinfo:
                if pcinfo[0][9] is None:
                    if team == 'N':
                        ctime = ''
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif team == 'N' and pcinfo[0][9] != 'N':
                    ctime = ''
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif pcinfo[0][9] != team:
                    query = query_update.format(owner, team, ctime, portal.guid)
                elif pcinfo[0][9] == team:
                    query = query_pureupdate.format(portal.guid)
                    ispureupdate = True
                else:
                    print("Failed to sync data for portal[{}]".format(portal.guid))
                    return False
                if ispureupdate:
                    print("Portal[{}] is found. No action is required.".format(portal.guid))
                else:
                    print("Portal[{}] is updated. Owner[{} --> {}]. Team[{} --> {}]. Capture Time[{} --> {}]."\
                            .format(portal.guid, pcinfo[0][8], owner, pcinfo[0][9], team, pcinfo[0][10], ctime))
            else:
                if portal.team == 'N':
                    ctime = ''
                query = query_insert.format(portal.guid, portal.id, portal.name, '', portal.lngE6, portal.latE6, owner, team, ctime, portal.raw)
                print("Portal[{}] is inserted.".format(portal.guid))
        cursor.execute(query)
        db.commit()
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)


def update_tile_sync_status(tilekey, syncfail=False):
    try:
        if syncfail:
            query_update = get_query(name="update_tilekey_status").format('E', tilekey)
            print('Tilekey[{}] sync is failed.'.format(tilekey))
        else:
            query_update = get_query(name="update_tilekey_status").format('Y', tilekey)
        db, cursor = connect_to_db()
        cursor.execute(query_update)
        db.commit()
        if syncfail is False:
            print('All portals in tilekey[{}] are updated.'.format(tilekey))
    except Exception as e:
        print(query_update)
        raise e
    finally:
        close_db(db, cursor)


def connect_to_db():
    d = xmlReader()
    dbinfo = d.getdbinfo()
    db = pymysql.connect(**dbinfo)
    cursor = db.cursor()
    return db, cursor


def close_db(db, cursor):
    if cursor:
        cursor.close()
    if db:
        db.close()


def get_query(name):
    d = xmlReader()
    return d.getquery(name)


if __name__ == '__main__':
    main()
