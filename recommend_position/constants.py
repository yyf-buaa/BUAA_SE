import os

thisDIR = os.path.dirname(__file__)
FACTOR_COLLECT = 10
FACTOR_BLACK = -10
FACTOR_LIKED = 0.5
FACTOR_COMMENT = 0.5
FACTOR_JOIN = 0.5
DB = os.path.dirname(thisDIR) + "/db.sqlite3"
dataPath = thisDIR + '/dataPos.p'
dataSumPath = thisDIR + '/dataPos_2.txt'
modelParams = thisDIR + '/Params/model_params.pkl'
featureData = thisDIR + '/Params/feature_data.pkl'
featureDict = thisDIR + '/Params/user_pos_dict.pkl'
epochs = 50
batch_size = 16
lr = 0.0005
