import ingrex
import pymysql
from datetime import datetime, timedelta
import time


def main():
    "main function"
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=8)
    print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start calculate tile keys...')
    r = ""
    try:
        query_select = "select PORTAL_LNGE6, PORTAL_LATE6 from ? where tile_key is null;"
        # print(query)
        db = pymysql.connect("")
        cursor = db.cursor()
        cursor.execute(query_select)
        r = cursor.fetchall()
        # print(r)
    except Exception as e:
        raise e
    finally:
        cursor.close()
        db.close()

    if r:
        for result in r:
            field = {
                'minLngE6': int(result[0]),
                'minLatE6': int(result[1]),
                'maxLngE6': int(result[0]),
                'maxLatE6': int(result[1]),
            }

            xtile, ytile = ingrex.Utils.calc_tile(field['minLngE6']/1E6, field['minLatE6']/1E6, 15)
            tilekey = '15_{}_{}_0_8_100'.format(xtile, ytile)
            try:
                query_update = "update ? set TILE_KEY = '" + tilekey + "', IS_SYNC = 'N' where PORTAL_LNGE6 = '" + result[0] + "' and PORTAL_LATE6 = '" + result[1] + "';"
                # print(query)
                cursor = db.cursor()
                cursor.execute(query_update)
                db.commit()
                print('Tilekey[{}] is updated.'.format(tilekey))
            except Exception as e:
                print(query_update)
                raise e
            finally:
                cursor.close()
                db.close()
    else:
        print('No record is found to calculate tilekey.')
    print('-' * 80)


if __name__ == '__main__':
    main()
