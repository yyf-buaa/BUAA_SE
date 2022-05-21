from torch.utils.data import Dataset
import pickle as pkl
import torch
import pandas as pd
import constants


class TravelDataset(Dataset):

    def __init__(self, pkl_file, drop_dup=False):
        df = pkl.load(open(pkl_file, 'rb'))
        if drop_dup:
            df_user = df.drop_duplicates(['userID'])
            df_movie = df.drop_duplicates(['itemID'])
            self.dataFrame = pd.concat((df_user, df_movie), axis=0)
        else:
            self.dataFrame = df

    def __len__(self):
        return len(self.dataFrame)

    def __getitem__(self, idx):

        # user data
        userID = self.dataFrame.iloc[idx]['userID']
        upositionID = self.dataFrame.iloc[idx]['upositionID']

        # travel data
        itemID = self.dataFrame.iloc[idx]['itemID']
        ipositionID = self.dataFrame.iloc[idx]['ipositionID']

        # target
        liked = self.dataFrame.iloc[idx]['liked']
        comment = self.dataFrame.iloc[idx]['comment']

        user_inputs = {
            'userID': torch.LongTensor([userID]).view(1, -1),
            'upositionID': torch.LongTensor([upositionID]).view(1, -1)
        }

        item_inputs = {
            'itemID': torch.LongTensor([itemID]).view(1, -1),
            'ipositionID': torch.LongTensor([ipositionID]).view(1, -1)
        }

        target = torch.FloatTensor([liked * constants.FACTOR_LIKED + comment * constants.FACTOR_COMMENT])

        sample = {
            'user_inputs': user_inputs,
            'item_inputs': item_inputs,
            'target': target
        }
        return sample
