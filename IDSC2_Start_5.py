#Standard library imports
import numpy as np
import pickle
import torch
import torchvision
import torchvision.transforms as transforms
from torch.autograd import Variable
import torch.nn.functional as F
from Xlib import display, X
import PIL.Image as Image
import time
import datetime
import pyautogui as pag
import cv2
import math
import random
import sys
from collections import namedtuple

#Custom imports
import ScreenCaptureMethods as SC 
import GameControlMethods as GC
import GameMemory as GM
import HyperParameters as HP
import VirtualStateMethods as VS
import CNN_2_AB22 as NN
import GameMemory as GM

def main(fileName):
    
    sys.stdout = open(fileName, 'w')

    #Allocating memory for game states
    board = np.zeros((20, 10), dtype= int)
    gameStateSPrime = np.ones((4,20,10), dtype= int)
    blockXY = np.zeros((4, 4, 2), dtype= int)

    #Hyperparamaters
    CAPACITY = HP.CAPACITY
    EPISODES = HP.EPISODES
    BATCH = HP.BATCH
    EPOCH = HP.EPOCH
    RESET = HP.RESET
    THRESHOLD = RESET
    THRESH_MIN = HP.THRESH_MIN
    CHECKPOINT = HP.CHECKPOINT
    DECAY = HP.DECAY
    LR = HP.LR
    DISCOUNT = HP.DECAY

    #Replay Memory and CNN

    #Unpickling version
    reader = open("KingCrimson3.5", 'rb')
    GERequiem = pickle.load(reader)
    reader.close()
    reader = open("Mithrandir3.5", 'rb')
    myCNN = pickle.load(reader)
    reader.close()

    #Reset pickle version
    #myCNN = NN.CNN2L()
    #GERequiem = GM.ReplayMemory(CAPACITY)

    #Starts the game
    pag.click(100,700)
    GC.startGame()
    playing = True

    epochBest = 0

    #Plays 1 game per epoch
    for epoch in range(1, EPISODES + 1):
        myScore = 0
        firstBlock = True
        while not SC.resetCheck() and playing:
        #for X in range(5):
            
            #Waits until a new piece enters the field, then immediately pauses
            pieceEnterCheck = False
            blockID = -1
            gameOver = False
            failSafe = 0
            while not pieceEnterCheck:
                failSafe += 1
                if failSafe > 50:
                    pag.hotkey("ctrl", "c")
                    NN.train(myCNN, BATCH, GERequiem, EPOCH, LR)
                    myScore = 0
                    pag.typewrite("nohighscore")
                    pag.press("enter")
                    THRESHOLD = RESET
                    playing = True
                    firstBlock = True
                    GC.startGame() 
                if gameOver:
                    break
                if SC.resetCheck():
                    """
                    NN.train(myCNN, BATCH, GERequiem, EPOCH, LR)
                    myScore = 0
                    pag.typewrite("nohighscore")
                    pag.press("enter")
                    THRESHOLD = RESET
                    playing = True
                    firstBlock = True
                    GC.startGame() 
                    """
                    gameOver = True        
                pieceEnterCheck, newPiece = SC.newPieceCheck(firstBlock)

            if gameOver:
                break
            pag.press("p")
            
            #Screen shots the field and identifies incoming piece
            board = SC.screenCap()
            #print("We are the board, resistance is futile, \n", board)
            blockID, rotations = SC.newPieceID(newPiece)
            board = VS.clearBadStart(board, blockID, firstBlock)
            #print("Bad start has been cleared, \n" , board)
            #print("Stop you've violated the law Identify yourself", blockID)

            #Returns up to 4 sets of XY coordinates from game states
            #Also plots those XY coordinates into a virtual field
            blockXY, gameStateSPrime = VS.StatePrime(blockID, board)

            #Used for memory storage
            initialState = np.copy(gameStateSPrime)
            initialBlockXY = np.copy(blockXY)

            #Checks for exploration
            if random.random() > THRESHOLD:

                #The chosen position for a rotation picked randomly among its best positions
                chosenPos = np.zeros(rotations)

                #The resulting height for the position after the block has been placed there
                blockHeights = np.zeros(rotations)

                #Select random positions initially and minimize reward array
                chosenPos.fill(-1)

                #Iterates all rotations
                for r in range(0, rotations):
                    
                    #Fits the game field into a properly sized torch tensor and feeds it into the CNN
                    boardHelper = torch.from_numpy(np.copy(gameStateSPrime[r]))
                    boardHelper = boardHelper.unsqueeze_(0)
                    boardHelper = boardHelper.unsqueeze_(0)
                    
                    #The CNN returns a 1 x 10 vector, each value corresponding to the predicted reward at each position
                    posVector = myCNN(boardHelper.float())
                    #print("CNN Output: ", posVector)

                    #Selects the best positions with max rewards from the CNN output, multiple best positions may exist
                    bestPositions = []
                    bestReward = -10000

                    #NOTICE: Reversed to MINIMUMU SELECTION <- OUTDATED
                    for i in range(10):
                        if posVector[0][i] == bestReward:
                            bestPositions.append(i)
                        if posVector[0][i] > bestReward:
                            bestReward = posVector[0][i]
                            bestPositions = []
                            bestPositions.append(i)
                    
                    #print("Pos Vector ", posVector)
                    #print("Best Reward in Vector ", bestReward)
                    #print("Index of best reward ", bestPositions)
                    #print("Best Index ", bestPositions)
                    #Picks a best position at random from tied best positions
                    chosenPos[r] = random.choice(bestPositions)

                    #Executes the position chosen in the virtual field
                    gameStateSPrime[r] = VS.virtualExecute(gameStateSPrime[r], blockXY[r], chosenPos[r])

                    blockHeights[r] = VS.height(gameStateSPrime[r], int(chosenPos[r]))

                #At this point, we've identified 4 possible States, found the best Action for each and calculated the State Prime for each

                #Stores the actual rewards generated by executing the above actions
                actualReward = np.zeros(rotations)
                savedBlockXYPrime = np.copy(blockXY)
                savedStatePrime = np.copy(gameStateSPrime)
                for r in range(rotations):
                    #Processes each State Prime for score calculation
                    actualReward[r] = VS.lineBreak(gameStateSPrime[r], blockHeights[r])

                #Previews the next block which will be Action Prime
                newBlockID, newBlockRot = SC.previewCap()
                
                #Creates a miniature Q-table to compare which chosenPos will lead to the best reward after factoring in Action Prime
                miniQ = np.zeros([rotations, newBlockRot])
                #The actual reward of the current Action is the basis for scoring Action Prime
                for r in range(rotations):
                    miniQ[r].fill(actualReward[r])

                #Copies gameStateSPrime since it is needed for memory storage later
                field = np.zeros((4,20,10)) * gameStateSPrime

                #Iterates over all rotations for current Action
                for r in range(rotations):

                    #Places the new block into State Prime, multiple versions because of different rotations
                    boardPrime, field = VS.StatePrime(newBlockID, field)

                    for rPrime in range(newBlockRot):
                        
                        #Creates a torch tensor to pass into the CNN
                        boardPrimeHelper = torch.from_numpy(np.ones((20,10)) * field[rPrime])
                        boardPrimeHelper = boardPrimeHelper.unsqueeze_(0)
                        boardPrimeHelper = boardPrimeHelper.unsqueeze_(0)
                        
                        #Gets the resultign vector from the CNN
                        posPrimeVector = myCNN(boardPrimeHelper.float())
                        
                        bestRewardPrime = -10000
                        for i in range(10):
                            if posPrimeVector[0][i] > bestRewardPrime:
                                bestRewardPrime = posPrimeVector[0][i]

                        #Adds discounted max future reward to miniQ table
                        miniQ[r][rPrime] = miniQ[r][rPrime] + DISCOUNT* bestRewardPrime

                #Finds the best current Action to take after factoring in future reward
                maxOfMaxs = np.zeros(rotations)
                
                #NOTICE: Reversed to MINIMUMU SELECTION <- OUTDATED
                #Finds the best possible reward after executing Action Prime
                for r in range(rotations):
                    maxOfMaxs[r] = np.max(miniQ[r])
                bestRewardPrime = np.max(maxOfMaxs)

                bestRots = []

                for r in range(rotations):
                    for rPrime in range(newBlockRot):
                        if miniQ[r][rPrime] == bestRewardPrime:
                            bestRots.append(r)

                #Selects the best rotation, randomly in the case of ties
                bestRot = random.choice(bestRots)
                actualReward[bestRot] = (actualReward[bestRot] + bestRewardPrime) if ((actualReward[bestRot] + bestRewardPrime) > actualReward[bestRot]) else actualReward[bestRot]

                #Accesses the State for the rotation, to be saved in memory
                currState = initialState[bestRot]

                #Accesses the chosen position for the rotation, to be saved in memoery
                currAction = chosenPos[bestRot]

                #Accesses the State Prime to be saved in memory
                nextState = gameStateSPrime[bestRot]

                #Executes action
                GC.order66(chosenPos[bestRot], bestRot)

                #Checks if the game ended, updating reward if so
                if SC.resetCheck():
                    playing = False
                    actualReward[bestRot] = -10000
                    #print("9 rings to kings of men who above all else desire tower")
                
                #Push to memory
                if not firstBlock:
                    GERequiem.push(currState, initialBlockXY[bestRot], currAction, nextState, actualReward[bestRot], myScore)
                firstBlock = False

                #Updates score tracker
                myScore = myScore + actualReward[bestRot] if not actualReward[bestRot] == -10000 else myScore
                #print("XY Coordinates before dropping, ", initialBlockXY[bestRot])
                #print("State before dropping\n", initialState[bestRot])
                #print("XY Coordinates after dropping, ", savedBlockXYPrime[bestRot])
                #print("State after dropping \n", savedStatePrime[bestRot])
                #print("Chosen Pos ", chosenPos[bestRot], " Chosen Rot ", bestRot, " Move Score ", actualReward[bestRot], "Total Score ", myScore, " Height ", blockHeights[bestRot])

            else:

                #Generates a random rotation and position
                randomPos, randomRot = VS.getRandomAction(blockID)
                
                #Saves the current state for memory storage
                currState = initialState[randomRot]
                #print("Current Random State\n", currState)

                #Performs the action in the virtual field; the block is move left/right and dropped
                nextState = VS.virtualExecute(np.copy(initialState[randomRot]), blockXY[randomRot], randomPos)
                #print("Current Random State after Dropping\n", nextState)
                #Finds the height of the block that was just dropped
                randomHeight = VS.height(nextState, randomPos)

                #Finds the reward for the action committed
                randomReward = VS.lineBreak(nextState, randomHeight)
                
                #Executes random action in the physical game
                GC.order66(randomPos, randomRot)

                #Checks if the game ended, updating reward if so
                if SC.resetCheck():
                    playing = False
                    randomReward = -10000
                    #print("9 rings to kings of men who above all else desire tower")

                #Push the random action to memory
                if not firstBlock:
                    GERequiem.push(currState, initialBlockXY[randomRot], randomPos, nextState, randomReward, myScore)
                firstBlock = False

                #Updates score tracker
                myScore = myScore + randomReward if not randomReward == -10000 else myScore
                #print("Random Pos ", randomPos, " Random Rot ", randomRot, " Move Score ", randomReward, " Total Score ", myScore, " Height ", randomHeight)
            
            #Decrement the probability of a random move occuring the longer the game goes
            if THRESHOLD > THRESH_MIN:
                THRESHOLD -= DECAY
        
        #Update the highest score per period of games and reset the tracker
        if myScore > epochBest:
            epochBest = myScore
        myScore = 0

        #Train after every game loss
        NN.train(myCNN, BATCH, GERequiem, EPOCH, LR)

        #Status report every certain number of games
        if (epoch + 1) % CHECKPOINT == 0:
            print("Speak friend and enter: ", epoch + 1, ", best score: ", epochBest)
            epochBest = -1
            writer = open("Mithrandir3.5", 'ab')
            pickle.dump(myCNN, writer)
            writer.close()
            writer = open("KingCrimson3.5", 'ab')
            pickle.dump(GERequiem, writer)
            writer.close()
            epochBest = 0
        
        #Restarts the tetris game
        pag.typewrite("nohighscore")
        pag.press("enter")
        THRESHOLD = RESET
        playing = True
        firstBlock = True
        GC.startGame()

    sys.stdout = sys.__stdout__
        
