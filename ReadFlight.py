import csv
import json
import os
import datetime
import pandas
# import pymysql

import sqlite3


# def readJson(filename, cursor, conn):
def readJson(filename, conn):
    f = open(filename, encoding="utf-8")
    file = json.load(f)
    if not file['result']['status'].__eq__("0"):
        return
    result = file['result']['result']

    # 出发/到达城市及代码
    city = filename.split('/')[-1].split('_')[0]
    city_code = result['city']
    endcity = filename.split('/')[-1].split('_')[1]
    date = result['date']
    endcity_code = result['endcity']

    flightList = result['list']

    date0 = pandas.to_datetime('2022-06-09', format='%Y-%m-%d')
    for i in range(2):

        for flight in flightList:
            flightno = flight['flightno']
            # 真实承运人
            realflightno = flight['realflightno']
            airline = flight['airline']

            # 机场及代码
            departport = flight['departport']
            departport_code = flight['departportcode']
            arrivalport = flight['arrivalport']
            arrivalport_code = flight['arrivalportcode']
            # 航站楼
            departterminal = flight['departterminal']
            arrivalterminal = flight['arrivalterminal']

            # 日期和时间

            date1 = pandas.to_datetime(flight['departdate'], format='%Y-%m-%d')
            date2 = pandas.to_datetime(flight['arrivaldate'], format='%Y-%m-%d')
            interval1 = date0 - date1
            departdate = (date1 + datetime.timedelta(days=+(interval1.days + i))).strftime("%Y-%m-%d")
            departtime = flight['departtime'] + ':00'
            arrivaldate = (date2 + datetime.timedelta(days=+(interval1.days+i))).strftime("%Y-%m-%d")
            arrivaltime = flight['arrivaltime'] + ':00'
            arrivaldateadd = flight['arrivaldateadd']

            # 飞机型号
            craft = flight['craft']
            # 经停站数
            stopnum = flight['stopnum']
            # 耗时
            costtime = flight['costtime']+':00'
            # 赚准点率95~95%
            punctualrate = flight['punctualrate']

            minprice = flight['minprice']
            airporttax = flight['airporttax']
            fueltax = flight['fueltax']
            # 有无餐食
            food = flight['food']
            # ASR支持标志
            isasr = flight['isasr']
            # 电子票
            iseticket = flight['iseticket']
            # 代码共享
            iscodeshare = flight['iscodeshare']

            # todo 加入Flight表
            sql1 = "insert into app_flight(flightno, realflightno, airline, city, city_code, endcity, endcity_code, departport, departport_code, arrivalport, arrivalport_code, departterminal, arrivalterminal, departdate, departtime, arrivaldate, arrivaltime, arrivaldateadd, craft, stopnum,costtime, punctualrate, minprice, airporttax, fueltax, food, isasr,  iseticket, iscodeshare) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') "
            rows = conn.execute(sql1 % (flightno,
                                        realflightno,
                                        airline,
                                        city,
                                        city_code,
                                        endcity,
                                        endcity_code,
                                        departport,
                                        departport_code,
                                        arrivalport,
                                        arrivalport_code,
                                        departterminal,
                                        arrivalterminal,
                                        departdate,
                                        departtime,
                                        arrivaldate,
                                        arrivaltime,
                                        arrivaldateadd,
                                        craft,
                                        stopnum,
                                        costtime,
                                        punctualrate,
                                        minprice,
                                        airporttax,
                                        fueltax,
                                        food,
                                        isasr,
                                        iseticket,
                                        iscodeshare))
            conn.commit()

            # 价格信息
            priceList = flight['pricelist']
            for cabinprice in priceList:
                cabinname = cabinprice['cabinname']
                cabincode = cabinprice['cabincode']
                price = cabinprice['price']
                discount = cabinprice['discount']
                #  todo 加入FlightPriceList表
                sql2 = "insert into app_flightpricelist(owner_id, cabinname, cabincode, price, discount) Values ((select id from app_flight where flightno='%s' and city='%s' and endcity='%s' and departdate='%s'), '%s', '%s', '%s', '%s')"
                rows = conn.execute(sql2 % (flightno, city, endcity, departdate,
                                            cabinname,
                                            cabincode,
                                            price,
                                            discount))
                conn.commit()

#
# # conn = pymysql.connect(host='127.0.0.1', user='root', password='123456', database='flightinfo')
# # cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

conn = sqlite3.connect(database='db.sqlite3')
# sql2 = "insert into app_appuser(name, password, cabincode, price, discount) Values ((select id from app_flight where flightno='%s' and city='%s' and endcity='%s'), '%s', '%s', '%s', '%s')"
# rows = conn.execute(sql2)
# conn.commit()
# cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
for root, dirs, files in os.walk("./flight_data/"):
    for f in files:
        # readJson(os.path.join(root, f), cursor, conn)
        readJson(os.path.join(root, f), conn)
# cursor.close()
conn.close()


