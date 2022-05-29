from torch.utils.data import Dataset
import pickle as pkl
import torch
import pandas as pd
import constants
from math import atan, pi


def getNorm(x):
    return atan(x) * 2 / pi


class PosDataset(Dataset):

    def __init__(self, pkl_file, drop_dup=False):
        df = pkl.load(open(pkl_file, 'rb'))
        if drop_dup:
            df_user = df.drop_duplicates(['userID'])
            df_pos = df.drop_duplicates(['itemID'])
            self.dataFrame = pd.concat((df_user, df_pos), axis=0)
        else:
            self.dataFrame = df

    def __len__(self):
        return len(self.dataFrame)

    def __getitem__(self, idx):

        # user data
        userID = self.dataFrame.iloc[idx]['userID']
        upositionID = self.dataFrame.iloc[idx]['upositionID']

        # pos data
        itemID = self.dataFrame.iloc[idx]['itemID']

        # target
        collect = self.dataFrame.iloc[idx]['collect']
        black = self.dataFrame.iloc[idx]['black']
        liked_travels_count = self.dataFrame.iloc[idx]['liked_travels_count']
        commented_travels_count = self.dataFrame.iloc[idx]['commented_travels_count']
        joined_companion_count = self.dataFrame.iloc[idx]['joined_companion_count']
        # 归一化 反正切

        user_inputs = {
            'userID': torch.LongTensor([userID]).view(1, -1),
            'upositionID': torch.LongTensor([upositionID]).view(1, -1)
        }

        item_inputs = {
            'itemID': torch.LongTensor([itemID]).view(1, -1)
        }

        target = torch.FloatTensor([collect * constants.FACTOR_COLLECT
                                    + black * constants.FACTOR_BLACK
                                    + getNorm(liked_travels_count) * constants.FACTOR_LIKED
                                    + getNorm(commented_travels_count) * constants.FACTOR_COMMENT
                                    + getNorm(joined_companion_count) * constants.FACTOR_JOIN])

        sample = {
            'user_inputs': user_inputs,
            'item_inputs': item_inputs,
            'target': target
        }
        return sample
