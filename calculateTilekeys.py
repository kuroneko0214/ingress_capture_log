import ingrex
import pymysql
from datetime import datetime, timedelta
import time
from ingrex.xmlReader import xmlReader


def main():
    "main function"
    d = xmlReader()
    tdelta = d.gettimedelta()
    cur_time = datetime.utcfromtimestamp(time.time()) + timedelta(hours=tdelta)
    print(cur_time.strftime('%Y-%m-%d %H:%M:%S'), '-- Start calculate tile keys...')
    r = ""
    try:
        query_select = d.getquery(name="select_coor_to_calculate")
        dbinfo = d.getdbinfo()
        db = pymysql.connect(**dbinfo)
        cursor = db.cursor()
        cursor.execute(query_select)
        r = cursor.fetchall()
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
            tilekey = d.gettilekeyformat().format(xtile, ytile)

            try:
                query_update = d.getquery(name="calculate_tilekey").format(tilekey, result[0], result[1])
                db = pymysql.connect(**dbinfo)
                cursor = db.cursor()
                cursor.execute(query_update)
                db.commit()
                print('Tilekey[{}] is updated.'.format(tilekey))
            except Exception as e:
                print(query_update)
                raise e
            finally:
                if cursor:
                    cursor.close()
                if db:
                    db.close()
    else:
        print('No record is found to calculate tilekey.')
    print('-' * 80)


if __name__ == '__main__':
    main()
