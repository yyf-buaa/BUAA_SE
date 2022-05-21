import os

thisDIR = os.path.dirname(__file__)
FACTOR_LIKED = 0.6
FACTOR_COMMENT = 0.4
DB = os.path.dirname(thisDIR) + "/db.sqlite3"
dataPath = thisDIR + '/dataTravel.p'
dataSumPath = thisDIR + '/dataTravel_2.txt'
modelParams = thisDIR + '/Params/model_params.pkl'
featureData = thisDIR + '/Params/feature_data.pkl'
featureDict = thisDIR + '/Params/user_travel_dict.pkl'
epochs = 50
batch_size = 16
lr = 0.0001
