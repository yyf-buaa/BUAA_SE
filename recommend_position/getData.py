import datetime
import pickle
import pandas as pd
import sqlite3
import numpy as np
import constants


def getData():
    db = sqlite3.connect(constants.DB)
    cursor = db.cursor()

    # user
    userList = dict()
    content = cursor.execute("SELECT id from app_appuser")
    for row in content:
        user = dict()
        user['userID'] = row[0]
        user['upositionID'] = 0
        userList[user['userID']] = user
    content_position = cursor.execute(
        "SELECT app_appuser.id, app_address.city_position_id from app_appuser, app_address WHERE app_appuser.position_id=app_address.id")
    for row in content_position:
        userList[row[0]]['upositionID'] = int(row[1][:-2])
    userList = sorted(userList.items(), key=lambda t: t[0])
    userList = dict(userList)
    # print(userList)

    # item
    itemList = dict()
    content = cursor.execute(
        "SELECT id from app_position WHERE id LIKE '%00'")
    cnt = 1
    map = {}
    for row in content:
        item = dict()
        item['itemID'] = int(row[0][:-2])
        itemList[cnt] = item
        map[item['itemID']] = cnt
        cnt = cnt + 1
    itemList = sorted(itemList.items(), key=lambda t: t[0])
    itemList = dict(itemList)

    # score
    # 地点收藏           0
    # 地点黑名单         1
    # 游记like记录       2
    # 游记comment记录    3
    # 同行加入

    score = np.zeros((max(itemList.keys()) + 1, max(userList.keys()) + 1, 5))

    # 地点收藏与黑名单
    content = cursor.execute("SELECT position_id, person_id, type from app_blackpos ")
    for row in content:
        if row[2] == '收藏':
            score[map[int(row[0][:-2])]][row[1]][0] = 1
        if row[2] == '黑名单':
            score[map[int(row[0][:-2])]][row[1]][1] = 1

    # 相关游记
    now = datetime.datetime.now()
    limit = now + datetime.timedelta(days=-15)
    content = cursor.execute("SELECT app_address.city_position_id, app_travel_likes.appuser_id "
                             "from app_travel_likes, app_travel, app_address "
                             "WHERE app_travel.position_id=app_address.id "
                             "AND app_travel.id=app_travel_likes.travel_id "
                             "AND app_travel.last_read>='%s' " % (limit.strftime("%Y-%m-%d")))
    for row in content:
        score[map[int(row[0][:-2])]][row[1]][2] += 1

    # comment记录
    content = cursor.execute("SELECT app_address.city_position_id, app_comment.owner_id "
                             "from app_comment, app_travel, app_address "
                             "where master_id is not NULL "
                             "AND master_id=app_travel.id "
                             "AND app_travel.position_id=app_address.id "
                             "AND app_travel.last_read>'%s' " % (limit.strftime("%Y-%m-%d")))
    for row in content:
        score[map[int(row[0][:-2])]][row[1]][3] += 1

    # companion加入
    content = cursor.execute("SELECT app_address.city_position_id, app_companion_fellows.appuser_id "
                             "from app_companion, app_companion_fellows, app_address "
                             "WHERE app_companion.id=app_companion_fellows.companion_id "
                             "AND app_companion.position_id=app_address.id "
                             "AND app_companion.end_time>'%s' " % (limit.strftime("%Y-%m-%d")))
    for row in content:
        score[map[int(row[0][:-2])]][row[1]][4] += 1

    dataList = pd.DataFrame()
    for pos in itemList.keys():
        for user in userList.keys():
            data = {}
            data.update(itemList[pos])
            data.update(userList[user])
            data['collect'] = score[pos][user][0]
            data['black'] = score[pos][user][1]
            data['liked_travels_count'] = score[pos][user][2]
            data['commented_travels_count'] = score[pos][user][3]
            data['joined_companion_count'] = score[pos][user][4]
            df = pd.DataFrame([data])
            dataList = dataList.append(df, ignore_index=True)

    cursor.close()
    output1 = open(constants.dataPath, 'wb')
    pickle.dump(dataList, output1)
    output1.close()
    output2 = open(constants.dataSumPath, 'w')
    output2.writelines(str(len(userList.items())) + ' ' + str(len(itemList.items())))
    output2.close()


getData()
