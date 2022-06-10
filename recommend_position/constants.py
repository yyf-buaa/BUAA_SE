import os

thisDIR = os.path.dirname(__file__)
FACTOR_COLLECT = 50
FACTOR_BLACK = -150
FACTOR_LIKED = 5
FACTOR_COMMENT = 5
FACTOR_JOIN = 5
DB = os.path.dirname(thisDIR) + "/db.sqlite3"
dataPath = thisDIR + '/dataPos.p'
dataSumPath = thisDIR + '/dataPos_2.txt'
modelParams = thisDIR + '/Params/model_params.pkl'
featureData = thisDIR + '/Params/feature_data.pkl'
featureDict = thisDIR + '/Params/user_pos_dict.pkl'
epochs = 70
batch_size = 16
lr = 0.0005
