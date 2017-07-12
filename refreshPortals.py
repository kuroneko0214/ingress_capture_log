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
    if islocal is False:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=tdelta)
    print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start refresh portals.')
    field = d.getfieldrange()
    s = requests.Session()
    guids = get_portal_guids()
    if len(guids) > 0:
        for i in range(0, len(guids)):
            if i >= 50:
                print('Select 50 guids to process...')
                break
            guid = guids[i][0]
            print(guid)
            with open(d.getcookiepath(islocal=islocal)) as cookies:
                cookies = cookies.read().strip()
            intel = Intel(cookies, field, s)
            result = ''
            try:
                result = intel.fetch_portal(guid)
            except Exception as e:
                backup_portal(guid)
                continue
            portal = ingrex.Portal(result, fromdetail=True)
            update_portal_details(guid, portal)
            time.sleep(30)
    else:
        print("No guid is found for refresh.")
    print('-' * 80)


def get_portal_guids():
    try:
        query_select = get_query(name="get_portal_gt7")
        db, cursor = connect_to_db()
        c = cursor.execute(query_select)
        r = cursor.fetchall()
        print('Get {} portal guid(s).'.format(c))
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)
    return r


def update_portal_details(guid, portal):
    try:
        query_select = get_query(name="select_portal_by_guid").format(guid)
        query_update = get_query(name="update_capture_time")
        query_update_utime = get_query(name="update_update_time").format(guid)
        db, cursor = connect_to_db()
        c = cursor.execute(query_select)
        if c == 1:
            r = cursor.fetchall()
            owner = r[0][8]
            team = r[0][9]
            ctime = r[0][10]
            new_ctime = ''
            if team != portal.team:
                if portal.team != "N":
                    new_ctime = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)
                    new_ctime = new_ctime.strftime('%Y-%m-%d %H:%M:%S')
                query_update = query_update.format(portal.owner, portal.team, new_ctime, guid)
                cursor.execute(query_update)
                db.commit()
                print("Portal[{}] information is updated. Previous updatetime is '{}', owner is '{}', team is '{}', capture time is '{}'. Now owner is '{}', team is '{}', capture time is '{}'.".format(guid, r[0][1], owner, team, ctime, portal.owner, portal.team, new_ctime))
            elif owner != portal.owner:
                new_ctime = ctime
                query_update = query_update.format(portal.owner, portal.team, new_ctime, guid)
                cursor.execute(query_update)
                db.commit()
                print("Portal[{}] information is updated. Previous updatetime is '{}', owner is '{}', team is '{}', capture time is '{}'. Now owner is '{}', team is '{}', capture time is '{}'.".format(guid, r[0][1], owner, team, ctime, portal.owner, portal.team, new_ctime))
            else:
                cursor.execute(query_update_utime)
                db.commit()
                print("Portal[{}] information is kept. Capture Time is '{}'.".format(guid, ctime))
        else:
            print("Portal[{}] information is not found.".format(guid))
    except Exception as e:
        raise e
    finally:
        close_db(db, cursor)


def backup_portal(guid):
    try:
        query_insert = get_query(name="backup_expired_portal").format(guid)
        query_delete = get_query(name="remove_expired_portal").format(guid)
        db, cursor = connect_to_db()
        cursor.execute(query_insert)
        db.commit()
        cursor.execute(query_delete)
        db.commit()
        print('Portal[{}] is removed from capture table.'.format(guid))
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
