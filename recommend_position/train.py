from model import rec_model_2
from dataset import PosDataset
from torch.utils.data import DataLoader, random_split
import torch
import torch.optim as optim
import torch.nn as nn
import constants
from getData import getData
from recInterface import savePosAndUserFeature

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

getData()

# --------------- hyper-parameters------------------
paramFile = open(constants.dataSumPath, 'r')
line = paramFile.readline()
line = line.split(' ')
paramFile.close()
total = int(line[0]) * int(line[1])

user_max_dict = {
    'userID': int(line[0]) + 1,
    'upositionID': 9999
}

item_max_dict = {
    'itemID': 9999
}

def train(model, num_epochs=50, lr=0.0001, batch_size=16):
    loss_function = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    datasets = PosDataset(pkl_file=constants.dataPath)
    train_data, eval_data = random_split(datasets, [round(0.9 * total), round(0.1 * total)],
                                         generator=torch.Generator().manual_seed(42))
    train_dataloader = DataLoader(datasets, batch_size=batch_size, shuffle=True)
    test_dataloader = DataLoader(eval_data, batch_size=batch_size, shuffle=True)

    losses = {'train': [], 'test': []}

    for epoch in range(num_epochs):
        loss_all = 0
        for i_batch, sample_batch in enumerate(train_dataloader):

            user_inputs = sample_batch['user_inputs']
            item_inputs = sample_batch['item_inputs']
            target = sample_batch['target'].to(device)

            model.zero_grad()

            tag_rank, _, _ = model(user_inputs, item_inputs)
            loss = loss_function(tag_rank, target)

            loss_all += loss
            loss.backward()
            optimizer.step()
        print('Epoch {}:\t loss:{}'.format(epoch, loss_all))
        losses['train'].append(loss_all.cpu().detach().numpy())
    # test
    loss_all = 0
    for i_batch, sample_batch in enumerate(test_dataloader):
        user_inputs = sample_batch['user_inputs']
        item_inputs = sample_batch['item_inputs']
        target = sample_batch['target'].to(device)

        model.zero_grad()

        tag_rank, _, _ = model(user_inputs, item_inputs)
        loss = loss_function(tag_rank, target)

        loss_all += loss
    losses['test'].append(loss_all.cpu().detach().numpy())
    print(losses)


if __name__ == '__main__':
    model = rec_model_2(user_max_dict=user_max_dict, item_max_dict=item_max_dict)
    model = model.to(device)

    # train model
    train(model=model, num_epochs=constants.epochs, lr=constants.lr, batch_size=constants.batch_size)
    torch.save(model.state_dict(), constants.modelParams)
    savePosAndUserFeature(model=model, batch_size=constants.batch_size)