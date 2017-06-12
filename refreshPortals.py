from ingrex import Intel, Utils
import ingrex, pymysql, time
import requests, sys
from datetime import datetime, timedelta


def main():
    "main function"
    reload(sys)
    sys.setdefaultencoding('utf-8')
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)
    print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start refresh portals.')
    field = {
        'minLngE6': ,
        'minLatE6': ,
        'maxLngE6': ,
        'maxLatE6': ,
    }
    s = requests.Session()
    guids = get_portal_guids()
    if len(guids) > 0:
        for i in range(0, len(guids)):
            if i >= 50:
                print('Select 50 guids to process...')
                break
            guid = guids[i][0]
            print(guid)
            with open('cookies') as cookies:
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
        query_select = "select distinct PORTAL_GUID from ? where DATEDIFF(NOW(),UPDATE_TIME) >= 8;"
        db = pymysql.connect("")
        cursor = db.cursor()
        c = cursor.execute(query_select)
        r = cursor.fetchall()
        print('Get {} portal guid(s).'.format(c))
    except Exception as e:
        raise e
    finally:
        cursor.close()
        db.close()
    return r


def update_portal_details(guid, portal):
    try:
        query_select = "select * from ? where PORTAL_GUID = '{}';".format(guid)
        query_update = "update ? set UPDATE_TIME = NOW(), PORTAL_OWNER = '{}', PORTAL_TEAM = '{}', CAPTURE_TIME = '{}' where PORTAL_GUID = '{}';"
        query_update_utime = "update ? set UPDATE_TIME = NOW() where PORTAL_GUID = '{}';".format(guid)
        db = pymysql.connect("")
        cursor = db.cursor()
        c = cursor.execute(query_select)
        if c == 1:
            r = cursor.fetchall()
            owner = r[0][8]
            team = r[0][9]
            ctime = r[0][10]
            new_ctime = ''
            if owner != portal.owner or team != portal.team:
                if portal.team != "N":
                    new_ctime = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)
                    new_ctime = new_ctime.strftime('%Y-%m-%d %H:%M:%S')
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
        cursor.close()
        db.close()


def backup_portal(guid):
    try:
        query_insert = "INSERT into ? select * from ? where portal_guid = '{}';".format(guid)
        query_delete = "DELETE from ? where PORTAL_GUID = '{}';".format(guid)
        db = pymysql.connect("")
        cursor = db.cursor()
        cursor.execute(query_insert)
        db.commit()
        cursor.execute(query_delete)
        db.commit()
        print('Portal[{}] is removed from capture table.'.format(guid))
    except Exception as e:
        raise e
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    main()
