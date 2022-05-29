from recommend import constants

import numpy as np
import pickle as pkl

def getUserLike(uid):
    feature_data = pkl.load(open(constants.featureData, 'rb'))
    user_item_ids = pkl.load(open(constants.featureDict, 'rb'))

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