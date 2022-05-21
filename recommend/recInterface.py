# Recommendation Interface

import torch
from torch.utils.data import DataLoader
from dataset import TravelDataset

import numpy as np
import pickle as pkl


def saveTravelAndUserFeature(model, batch_size):
    datasets = TravelDataset(pkl_file='dataTravel.p', drop_dup=True)
    dataloader = DataLoader(datasets, batch_size=batch_size, shuffle=False, num_workers=4)

    user_feature_dict = {}
    item_feature_dict = {}
    items = {}
    users = {}
    with torch.no_grad():
        for i_batch, sample_batch in enumerate(dataloader):
            user_inputs = sample_batch['user_inputs']
            item_inputs = sample_batch['item_inputs']

            # B x 1 x 200 = 256 x 1 x 200
            _, feature_user, feature_item = model(user_inputs, item_inputs)

            # B x 1 x 200 = 256 x 1 x 200
            feature_user = feature_user.cpu().numpy()
            feature_item = feature_item.cpu().numpy()

            for i in range(user_inputs['userID'].shape[0]):
                userID = user_inputs['userID'][i]
                upositionID = user_inputs['upositionID'][i]

                itemID = item_inputs['itemID'][i]
                ipositionID = item_inputs['ipositionID'][i]

                if userID.item() not in users.keys():
                    users[userID.item()] = {'userID': userID, 'upositionID': upositionID}
                if itemID.item() not in items.keys():
                    items[itemID.item()] = {'itemID': itemID, 'ipositionID': ipositionID}

                if userID.item() not in user_feature_dict.keys():
                    user_feature_dict[userID.item()] = feature_user[i]
                if itemID.item() not in item_feature_dict.keys():
                    item_feature_dict[itemID.item()] = feature_item[i]

            print('Solved: {} samples'.format((i_batch + 1) * batch_size))
    feature_data = {'feature_user': user_feature_dict, 'feature_item': item_feature_dict}
    dict_user_travel = {'user': users, 'item': items}
    print(len(dict_user_travel['user']))
    print(len(feature_data['feature_item']))
    pkl.dump(feature_data, open('Params/feature_data.pkl', 'wb'))
    pkl.dump(dict_user_travel, open('Params/user_travel_dict.pkl', 'wb'))


'''
临近的用户or游记 K推荐个数
# getKNNitem(ID, 'user', 2)  # userID=ID的相似用户
# getKNNitem(ID, 'item', 3)  # itemID=ID的相似游记
'''


# 记得检查ID是否存在
def getKNNitem(itemID, itemName, K=1):

    # get cosine similarity between vec1 and vec2
    def getCosineSimilarity(vec1, vec2):
        cosine_sim = float(vec1.dot(vec2.T).item()) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return cosine_sim

    # 加载用户特征or游记特征
    feature_data = pkl.load(open('Params/feature_data.pkl', 'rb'))
    feature_items = feature_data['feature_' + itemName]
    feature_current = feature_items[itemID]

    id_sim = [(item_id, getCosineSimilarity(feature_current, vec2)) for item_id, vec2 in feature_items.items()]
    id_sim = sorted(id_sim, key=lambda x: x[1], reverse=True)

    return [id_sim[i][0] for i in range(K + 1)][1:]


# 获取用户对游记喜爱顺序
def getUserLike(uid):
    feature_data = pkl.load(open('Params/feature_data.pkl', 'rb'))
    user_item_ids = pkl.load(open('Params/user_travel_dict.pkl', 'rb'))

    feature_user = feature_data['feature_user'][uid]

    item_dict = user_item_ids['item']
    mid_rank = {}
    for mid in item_dict.keys():
        feature_item = feature_data['feature_item'][mid]
        rank = np.dot(feature_user, feature_item.T)
        print(rank)
        if mid not in mid_rank.keys():
            mid_rank[mid] = rank.item()

    mid_rank = [(mid, rank) for mid, rank in mid_rank.items()]
    mids = [mid[0] for mid in sorted(mid_rank, key=lambda x: x[1], reverse=True)]

    return mids

