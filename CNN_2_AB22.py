import numpy as np
import torch
import random
import torchvision
import torchvision.transforms as transforms
from torch.utils.data.sampler import SubsetRandomSampler
from torch.autograd import Variable
import torch.nn.functional as F
from sklearn import svm
import torch.optim as optim
from collections import namedtuple
import time
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import VirtualStateMethods as VS

classes = {'0','1','2','3','4','5','6','7','8','9'}

#inheriting torch
#Question 2.5? one layer too much and one layer too little
class CNN2L(torch.nn.Module):

    #2x28,28?

    #constructor declaration?
    def __init__(self):
        super(CNN2L, self).__init__()

        self.conv1 = torch.nn.Conv2d(1, 30, kernel_size = 1, stride = 1, padding = 0)
        self.pool1 = torch.nn.MaxPool2d(kernel_size = 1, stride = 1, padding = 0)

        #input ch = 3 output = 20
        #no loss of size in the image
        self.conv2 = torch.nn.Conv2d(30, 30, kernel_size = 5, stride = 1, padding = 2)

        #image size is rediced to half x half y dim
        self.pool2 = torch.nn.MaxPool2d(kernel_size = 2, stride = 2, padding = 0)

        #3>20 potentially
        self.conv3 = torch.nn.Conv2d(30, 1, kernel_size = 3, stride = 1, padding = 1)
        self.pool3 = torch.nn.MaxPool2d(kernel_size = 2, stride = 1, padding= 1)

        self.fc1 = torch.nn.Linear(10*5, 100)
        self.fc2 = torch.nn.Linear(100, 100)
        self.fc3 = torch.nn.Linear(100, 10)
        #self.fc4 = torch.nn.Linear(10, 10)

    def forward(self, X):

        #28*28*3 > 14*14*20
        X = F.relu(self.conv1(X))
        X = self.pool1(X)

        #14*14*20 > 7*7*20
        X = F.relu(self.conv2(X))
        X = self.pool2(X)
        
        X = F.relu(self.conv3(X))
        #X = self.pool3(X)
        #20*
        X = X.view(-1, 5*10)

        X = F.relu(self.fc1(X))

        X = self.fc2(X)

        X = self.fc3(X)

        #X = self.fc4(X)
        #print("X at fc4 ", X.shape)

        #X = max(X)

        return(X)

def lossAndOptimizationFunction(net, learningRate = 0.01):

        optimizer = optim.RMSprop(net.parameters(), lr = learningRate)
        loss = nn.MSELoss()

        return optimizer, loss

#Take this out to main file
def train(net, batchSize, REPLAYMEMORY, epochs, learningRate):

        if batchSize > REPLAYMEMORY.__len__():
            return

        #print("#####################################")

        train = REPLAYMEMORY.sample(batchSize)

        optimizer, loss = lossAndOptimizationFunction(net, learningRate)

        for e in range(epochs):
            
            curLoss = 0.0
            totalTrainLoss = 0

            prediction = np.zeros((batchSize, 1, 10))
            actual = np.zeros((batchSize, 1, 10))

            for i, data in enumerate(train,0):

                state, rot, action, next_state, reward, base = data

                boardHelper = torch.from_numpy(np.ones((20,10)) * state)
                boardHelper = boardHelper.unsqueeze_(0)
                boardHelper = boardHelper.unsqueeze_(0)
                action = int(action)
                outputs = net(boardHelper.float())
                prediction[i][0] = outputs.detach().numpy()

                for pos in range(10):
                    nextState = np.copy(state)
                    nextState = VS.virtualExecute(nextState, rot, pos)
                    h = VS.height(nextState, pos)

                    actual[i][0][pos] = VS.lineBreak(nextState, h) + base


                #actual[i][0][action] = reward + base
                #print("Actual ", actual[i][0])
                #print("Prediction ", prediction[i][0])
            
            optimizer.zero_grad()
            prediction = Variable(torch.from_numpy(prediction), requires_grad=True)
            actual = Variable(torch.from_numpy(actual), requires_grad=True)
            loss_size = loss(prediction, actual)
            #print(loss_size.data)
            loss_size.backward()
            optimizer.step()
            curLoss += loss_size.data
            totalTrainLoss += loss_size.data
            train = REPLAYMEMORY.sample(batchSize)

#CNN = CNN2L()

#train(CNN, 32, 5, 0.001)












