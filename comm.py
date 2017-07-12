"COMM monitor"
import ingrex
import time, pymysql
import sys, requests
from datetime import datetime, timedelta
from ingrex.xmlReader import xmlReader


def main():
    "main function"
    islocal = False
    d = xmlReader()
    tdelta = d.gettimedelta()
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=tdelta)
    cur_time = cur_time.strftime('%Y-%m-%d %H:%M:%S')
    print('{} -- Start Logging...'.format(cur_time))
    if islocal is False:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    field = d.getfieldrange()
    mints = get_max_timestamp()
    maxts = int(time.time() * 1000)
    l_mints = maxts

    print('The overall timestamp duration is {}~{}.'.format(mints, maxts))
    result = ''
    s = requests.Session()

    with open(d.getcookiepath(islocal=islocal)) as cookies:
        cookies = cookies.read().strip()
    intel = ingrex.Intel(cookies, field, s)
    update_maxts(int(maxts))
    while True:
        result = intel.fetch_msg(mints=int(mints), maxts=int(maxts))
        if result:
            for item in result[::-1]:
                message = ingrex.Message(item)
                ts = int(message.timestamp)
                if ts <= l_mints:
                    l_mints = ts
                print('{} {} {}'.format(message.time, message.team, message.text))

                if message.player_action.strip() in d.getactions():
                    insert_comm(message)
                    portal_guid = fetch_portal_guid(message)
                    if portal_guid == "":
                        insert_for_update(message)
                    else:
                        portal_raw = intel.fetch_portal(guid=portal_guid)
                        portal = ingrex.Portal(portal_raw, fromdetail=True)
                        if message.player_action.strip() == 'captured':
                            update_capture_status(message, portal)
                        else:
                            update_capture_status(message, portal, iscapture=False)
            print('Fetched {} comm logs during the timestamp period {}~{}.'.format(len(result), int(l_mints), int(maxts)))
            print('+' * 80)
        else:
            print('No result can be fetched during the period {}~{}. Exit...'.format(mints, maxts))
            break
        if len(result) < 50:
            break
        if mints != l_mints:
            mints, maxts = mints, l_mints - 1
        else:
            break
        time.sleep(20)

    print('-' * 80)


def update_maxts(maxts):
    try:
        db, cursor = connect_to_db()
        query = get_query(name="update_maxts").format(maxts)
        cursor.execute(query)
        db.commit()
    except Exception as e:
        print(query)
        raise e
    finally:
        close_db(db, cursor)


def get_max_timestamp():
    try:
        db, cursor = connect_to_db()
        query = get_query(name="get_max_ts")
        cursor.execute(query)
        r = cursor.fetchall()[0][0]
    except Exception as e:
        print('Failed to fetch max timestamp.')
        raise e
    finally:
        close_db(db, cursor)

    if r:
        if int(time.time() * 1000) - int(r) > 240000:
            print("Timestamp is too old(earlier than current timestamp minus 4 mins): {}".format(r))
            r = int(time.time() * 1000 - 120000)
            print("Use current timestamp minus 2 mins: {}".format(r))
        else:
            r = int(r) + 1
            print("Max timestamp is found. Plus 1ms for use: {}".format(r))
    else:
        r = int(time.time() * 1000 - 240000)
        print("Timestamp is not found. Use current timestamp minus 4 mins: {}".format(r))
    return int(r)


def insert_comm(message):
    try:
        db, cursor = connect_to_db()
        query = get_query(name="insert_comm")\
            .format(message.time, message.timestamp, message.player_team, message.player_name, message.player_action, message.portal_name, message.portal_addr, message.portal_lngE6, message.portal_latE6, message.portal_text, message.raw)
        cursor.execute(query)
        db.commit()
    except Exception as e:
        print(query)
        raise e
    finally:
        close_db(db, cursor)


def fetch_portal_guid(message):
    portal_guid = ""
    try:
        db, cursor = connect_to_db()
        query = get_query(name="fetch_portal_guid")\
            .format(message.portal_lngE6, message.portal_latE6, message.portal_name)
        cnt = cursor.execute(query)
        if cnt == 1:
            r = cursor.fetchall()
            portal_guid = r[0][0]
            print('Portal GUID[{}] is found.'.format(portal_guid))
        else:
            print('Portal[{} {}] GUID is not found.'.format(message.portal_lngE6, message.portal_latE6))
    except Exception as e:
        print(query)
        raise e
    finally:
        close_db(db, cursor)
    return portal_guid


def update_capture_status(message, portal, iscapture=True):
    query_capture = get_query(name="update_capture_status")\
        .format(message.time, message.portal_addr, portal.owner, portal.team, message.time, portal.lngE6, portal.latE6, portal.name)
    query_refresh = get_query(name="refresh_update_time")\
        .format(message.time, message.portal_addr, portal.owner, portal.team, portal.lngE6, portal.latE6, portal.name)
    query_select = get_query(name="select_portal_by_detail")\
        .format(portal.lngE6, portal.latE6, portal.name)
    try:
        db, cursor = connect_to_db()
        cursor.execute(query_select)
        r = cursor.fetchall()
        if time.strptime(r[0][1], '%Y-%m-%d %H:%M:%S') > time.strptime(message.time, '%Y-%m-%d %H:%M:%S'):
            print('Portal[{} {}] status is NOT updated. Time[{}] is too old[{}].'.format(portal.lngE6, portal.latE6, message.time, r[0][1]))
        else:
            if iscapture:
                cursor.execute(query_capture)
            else:
                owner = r[0][8]
                if portal.owner != owner:
                    cursor.execute(query_capture)
                else:
                    cursor.execute(query_refresh)
            db.commit()
            print('Portal[{} {}] status is updated'.format(portal.lngE6, portal.latE6))
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)


def insert_for_update(message):
    print('Ready to insert for update.')
    try:
        query_select = get_query(name="select_portal_in_tilekey")\
            .format(message.portal_lngE6, message.portal_latE6, message.portal_name)
        query_insert = get_query(name="insert_tilekey")\
            .format(message.time, message.timestamp, message.player_team, message.player_name, message.player_action, message.portal_name, message.portal_addr, message.portal_lngE6, message.portal_latE6)
        query_update = get_query(name="update_tilekey")\
            .format(message.time, message.timestamp, message.player_team, message.player_name, message.player_action, message.portal_addr, message.portal_lngE6, message.portal_latE6, message.portal_name)
        db, cursor = connect_to_db()
        r = cursor.execute(query_select)
        if r == 1:
            c = cursor.fetchall()
            if time.strptime(c[0][1], '%Y-%m-%d %H:%M:%S') > time.strptime(message.time, '%Y-%m-%d %H:%M:%S'):
                print('Portal[{} {}] is NOT refreshed because TIME[{}] is too old[{}].'.format(message.portal_lngE6, message.portal_latE6, message.time, c[0][1]))
            else:
                cursor.execute(query_update)
                db.commit()
                print('Portal[{} {}] is refreshed in temp table.'.format(message.portal_lngE6, message.portal_latE6))
        else:
            cursor.execute(query_insert)
            db.commit()
            print('Portal[{} {}] is inserted, it will be updated later.'.format(message.portal_lngE6, message.portal_latE6))
    except Exception as e:
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
