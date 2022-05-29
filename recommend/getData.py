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

    # item
    itemList = dict()
    content = cursor.execute(
        "SELECT app_travel.id, app_address.city_position_id from app_travel, app_address WHERE app_travel.position_id=app_address.id")
    for row in content:
        item = dict()
        item['itemID'] = row[0]
        item['ipositionID'] = int(row[1][:-2])
        itemList[item['itemID']] = item
    itemList = sorted(itemList.items(), key=lambda t: t[0])
    itemList = dict(itemList)

    # score
    # 莫得read记录
    # like记录

    score = np.zeros((max(itemList.keys()) + 1, max(userList.keys()) + 1, 2))
    content = cursor.execute("SELECT travel_id, appuser_id from app_travel_likes")
    for row in content:
        score[row[0]][row[1]][0] = 1
    # comment记录
    content = cursor.execute("SELECT master_id, owner_id from app_comment where master_id is not NULL ")
    for row in content:
        score[row[0]][row[1]][1] = 1

    dataList = pd.DataFrame()
    for travel in itemList.keys():
        for user in userList.keys():
            data = {}
            data.update(itemList[travel])
            data.update(userList[user])
            data['liked'] = score[travel][user][0]
            data['comment'] = score[travel][user][1]
            df = pd.DataFrame([data])
            dataList = dataList.append(df, ignore_index=True)

    cursor.close()
    output1 = open(constants.dataPath, 'wb')
    pickle.dump(dataList, output1)
    output1.close()
    output2 = open(constants.dataSumPath, 'w')
    output2.writelines(str(len(userList.items())) + ' ' + str(len(itemList.items())))
    output2.close()