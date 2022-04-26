import csv
import datetime
import json
import os
import sqlite3

import pandas


def dateCal(day, date):
    dayadd = day - 1
    return (date + datetime.timedelta(days=+dayadd)).strftime("%Y-%m-%d")


def readTrain(filename, conn):
    f = open(filename, encoding="utf-8")
    file = json.load(f)

    if not file['result']['status'].__eq__("0"):
        return
    result = file['result']['result']

    trainno = result['trainno']
    startstation = result['startstation']
    endstation = result['endstation']
    type = result['type']
    typename = result['typename']
    date = pandas.to_datetime("2022-4-5", format='%Y-%m-%d')
    # print(date + datetime.timedelta(days=+1))
    startdate = date.strftime("%Y-%m-%d")
    stationList = result['list']
    list_len = len(stationList)
    for i in range(list_len):
        # 一条列车信息
        if i == list_len - 1:
            # 最后一个
            return
        departInfo = stationList[i]
        departure = departInfo['station']
        day = departInfo['day']
        departdate = dateCal(day, date)
        departtime = departInfo['departuretime']
        costtime1 = departInfo['costtime']
        stoptime1 = departInfo['stoptime']
        sequenceno1 = departInfo['sequenceno']

        # 座价
        pricesw_1 = departInfo['pricesw']  # 商务座
        pricetd_1 = departInfo['pricetd']
        pricerz_1 = departInfo['pricerz']  # 软座
        priceyz_1 = departInfo['priceyz']  # 硬座
        pricegr1_1 = departInfo['pricegr1']  # 高级软卧上铺
        pricegr2_1 = departInfo['pricegr2']  # 高级软卧下铺
        pricerw1_1 = departInfo['pricerw1']  # 软卧上铺
        pricerw2_1 = departInfo['pricerw2']  # 软卧下铺
        priceyw1_1 = departInfo['priceyw1']  # 硬卧上铺
        priceyw2_1 = departInfo['priceyw2']  # 硬卧中铺
        priceyw3_1 = departInfo['priceyw3']  # 硬卧下铺
        priceyd_1 = departInfo['priceyd']  # 一等座
        priceed_1 = departInfo['priceed']  # 二等座
        for j in range(i + 1, list_len):
            arrivalInfo = stationList[j]
            arrival = arrivalInfo['station']
            day2 = arrivalInfo['day']
            arrivaldate = dateCal(day2, date)
            arrivaltime = arrivalInfo['arrivaltime']
            costtime2 = arrivalInfo['costtime']
            costtime = costtime2 - costtime1 - stoptime1  # 分钟
            costtime = str(costtime // 60) + "h" + str(costtime % 60) + "min"
            stopnum = arrivalInfo['sequenceno'] - sequenceno1 - 1
            intoday = day2 - day + 1
            # 先计入Train表
            sql1 = "insert into app_train(trainno, departstation, terminalstation, type, typename, station, endstation, departdate, departtime, arrivaldate, arrivaltime, stopnum, costtime, day) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s') "
            rows = conn.execute(sql1 % (trainno,
                                        startstation,
                                        endstation,
                                        type,
                                        typename,
                                        departure,
                                        arrival,
                                        departdate,
                                        departtime,
                                        arrivaldate,
                                        arrivaltime,
                                        stopnum,
                                        costtime, intoday))
            conn.commit()
            pricesw_2 = arrivalInfo['pricesw']  # 商务座
            pricetd_2 = arrivalInfo['pricetd']
            pricerz_2 = arrivalInfo['pricerz']  # 软座
            priceyz_2 = arrivalInfo['priceyz']  # 硬座
            pricegr1_2 = arrivalInfo['pricegr1']  # 高级软卧上铺
            pricegr2_2 = arrivalInfo['pricegr2']  # 高级软卧下铺
            pricerw1_2 = arrivalInfo['pricerw1']  # 软卧上铺
            pricerw2_2 = arrivalInfo['pricerw2']  # 软卧下铺
            priceyw1_2 = arrivalInfo['priceyw1']  # 硬卧上铺
            priceyw2_2 = arrivalInfo['priceyw2']  # 硬卧中铺
            priceyw3_2 = arrivalInfo['priceyw3']  # 硬卧下铺
            priceyd_2 = arrivalInfo['priceyd']  # 一等座
            priceed_2 = arrivalInfo['priceed']  # 二等座

            if (pricesw_1 == "-" or sequenceno1 == 1) and (not pricesw_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "商务座", pricesw_2))
                conn.commit()
            elif (not pricesw_1 == "-") and (not pricesw_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "商务座", pricesw_2 - pricesw_1))
                conn.commit()

            if (pricetd_1 == "-" or sequenceno1 == 1) and (not pricetd_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "特等座", pricetd_2))
                conn.commit()
            elif (not pricetd_1 == "-") and (not pricetd_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "特等座", pricetd_2 - pricetd_1))
                conn.commit()

            if (pricerz_1 == "-" or sequenceno1 == 1) and (not pricerz_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软座", pricerz_2))
                conn.commit()
            elif (not pricerz_1 == "-") and (not pricerz_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软座", pricerz_2 - pricerz_1))
                conn.commit()

            if (priceyz_1 == "-" or sequenceno1 == 1) and (not priceyz_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬座", priceyz_2))
                conn.commit()
            elif (not priceyz_1 == "-") and (not priceyz_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬座", priceyz_2 - priceyz_1))
                conn.commit()

            if (pricegr1_1 == "-" or sequenceno1 == 1) and (not pricegr1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "高级软卧上铺", pricegr1_2))
                conn.commit()
            elif (not pricegr1_1 == "-") and (not pricegr1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "高级软卧上铺", pricegr1_2 - pricegr1_1))
                conn.commit()

            if (pricegr2_1 == "-" or sequenceno1 == 1) and (not pricegr2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "高级软卧下铺", pricegr2_2))
                conn.commit()
            elif (not pricegr2_1 == "-") and (not pricegr2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "高级软卧下铺", pricegr2_2 - pricegr2_1))
                conn.commit()

            if (pricerw1_1 == "-" or sequenceno1 == 1) and (not pricerw1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软卧上铺", pricerw1_2))
                conn.commit()
            elif (not pricerw1_1 == "-") and (not pricerw1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软卧上铺", pricerw1_2 - pricerw1_1))
                conn.commit()

            if (pricerw2_1 == "-" or sequenceno1 == 1) and (not pricerw2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软卧下铺", pricerw2_2))
                conn.commit()
            elif (not pricerw2_1 == "-") and (not pricerw2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "软卧下铺", pricerw2_2 - pricerw2_1))
                conn.commit()

            if (priceyw1_1 == "-" or sequenceno1 == 1) and (not priceyw1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧上铺", priceyw1_2))
                conn.commit()
            elif (not priceyw1_1 == "-") and (not priceyw1_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧上铺", priceyw1_2 - priceyw1_1))
                conn.commit()

            if (priceyw2_1 == "-" or sequenceno1 == 1) and (not priceyw2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧中铺", priceyw2_2))
                conn.commit()
            elif (not priceyw2_1 == "-") and (not priceyw2_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧中铺", priceyw2_2 - priceyw2_1))
                conn.commit()

            if (priceyw3_1 == "-" or sequenceno1 == 1) and (not priceyw3_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧下铺", priceyw3_2))
                conn.commit()
            elif (not priceyw3_1 == "-") and (not priceyw3_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "硬卧下铺", priceyw3_2 - priceyw3_1))
                conn.commit()

            if (priceyd_1 == "-" or sequenceno1 == 1) and (not priceyd_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "一等座", priceyd_2))
                conn.commit()
            elif (not priceyd_1 == "-") and (not priceyd_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "一等座", priceyd_2 - priceyd_1))
                conn.commit()

            if (priceed_1 == "-" or sequenceno1 == 1) and (not priceed_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "二等座", priceed_2))
                conn.commit()
            elif (not priceed_1 == "-") and (not priceed_2 == "-"):
                sql2 = "insert into app_trainpricelist(owner_id, type, price) Values ((select id from app_train where trainno='%s' and station='%s' and endstation='%s'), '%s', '%s')"
                rows = conn.execute(sql2 % (trainno, departure, arrival, "二等座", priceed_2 - priceed_1))
                conn.commit()


conn = sqlite3.connect(database='db.sqlite3')
for root, dirs, files in os.walk("./train_data/"):
    for f in files:
        readTrain(os.path.join(root, f), conn)
# readTrain("./train_data/2152.json", conn)
conn.close()
