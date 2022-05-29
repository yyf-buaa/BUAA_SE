import torch
import torch.nn as nn
import torch.nn.functional as F

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


class rec_model_2(nn.Module):

    def __init__(self, user_max_dict, item_max_dict, embed_dim=32, fc_size=100):
        super(rec_model_2, self).__init__()

        # --------------------------------- user channel ----------------------------------------------
        # user embeddings 嵌入层
        self.embedding_userID = nn.Embedding(user_max_dict['userID'], embed_dim)
        self.embedding_upositionID = nn.Embedding(user_max_dict['upositionID'], embed_dim)

        # user embedding to fc: the first dense layer 全连接层1
        self.fc_userID = nn.Linear(embed_dim, embed_dim)
        self.fc_upositionID = nn.Linear(embed_dim, embed_dim)

        # concat embeddings to fc: the second dense layer 全连接层2
        self.fc_user_combine = nn.Linear(2 * embed_dim, fc_size)

        # --------------------------------- item channel ---------------------------------------------
        # item embeddings 嵌入层
        self.embedding_itemID = nn.Embedding(item_max_dict['itemID'], embed_dim)
        # 若要用tag进行推荐采取 mode='sum'

        # 全连接层1  1*64
        self.fc_itemID = nn.Linear(embed_dim, embed_dim)

        # 全连接层2  1*100
        self.fc_item_combine = nn.Linear(embed_dim, fc_size)

        # BatchNorm layer 网络加速
        self.BN_userID = nn.BatchNorm2d(1)
        self.BN_upositionID = nn.BatchNorm2d(1)

        self.BN_itemID = nn.BatchNorm2d(1)

    def forward(self, user_input, item_input):
        # pack train_data
        userID = user_input['userID']
        upositionID = user_input['upositionID']

        itemID = item_input['itemID']

        if torch.cuda.is_available():
            userID, upositionID, itemID = \
                userID.to(device), upositionID.to(device), itemID.to(device)

        # user channel  1 x 64
        feature_userID = self.BN_userID(F.relu(self.fc_userID(self.embedding_userID(userID))))
        feature_upositionID = self.BN_upositionID(F.relu(self.fc_upositionID(self.embedding_upositionID(upositionID))))

        # feature_user  B x 1 x 100
        feature_user = F.tanh(self.fc_user_combine(torch.cat([feature_userID, feature_upositionID], 3))) \
            .view(-1, 1, 100)

        # item channel  1 x 64
        feature_itemID = self.BN_itemID(F.relu(self.fc_itemID(self.embedding_itemID(itemID))))

        # feature_item B x 1 x 100
        feature_item = F.tanh(self.fc_item_combine(torch.cat([feature_itemID], 3))) \
            .view(-1, 1, 100)

        output = torch.sum(feature_user * feature_item, 2)  # B x rank
        return output, feature_user, feature_item
