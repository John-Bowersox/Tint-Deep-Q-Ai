import numpy as np
import random
import math

#Determines height MAY NEED EDITING
def height(field, pos):
    h = 0
    for height in range(20):
        if field[height][pos] == 1:
            h = height
            break
    return 20-h

#Returns a random action
def getRandomAction(ID):
    rots = np.array([2,2,4,4,4,2,1])
    return random.randint(0,9), random.randint(0, rots[ID]-1)

#Clears a lagging start  off the board
def clearBadStart(field, ID, firstBlock):
    
    height = 1 if firstBlock else 0

    #Long ID = 0
    if ID == 0:

        field[height+1][3] = 0
        field[height+1][4] = 0
        field[height+1][5] = 0
        field[height+1][6] = 0
    
    #Z ID = 1
    elif ID == 1:

        field[height][3] = 0
        field[height][4] = 0
        field[height+1][4] = 0
        field[height+1][5] = 0

    #T ID = 2
    elif ID == 2:

        field[height+1][3] = 0
        field[height+1][4] = 0
        field[height+1][5] = 0
        field[height+2][4] = 0

    #L ID = 3
    elif ID == 3:

        field[height+1][3] = 0
        field[height+1][4] = 0
        field[height+1][5] = 0
        field[height+2][3] = 0

    #J ID = 4
    elif ID == 4:

        field[height+1][3] = 0
        field[height+1][4] = 0
        field[height+1][5] = 0
        field[height+2][5] = 0

    #S ID = 5
    elif ID == 5:

        field[height][4] = 0
        field[height][5] = 0
        field[height+1][3] = 0
        field[height+1][4] = 0

    #Square ID =6
    elif ID == 6:

        field[height][3] = 0
        field[height][4] = 0
        field[height+1][3] = 0
        field[height+1][4] = 0

    return field


#Processes the playing field after the move has been executed virtually.
def lineBreak(field, h):

    #Checks if the Game has ended, massive penalty if so
    #if endCheck(field):
    #    print("7 to the dwarves in halls of stone")
    #    return -10000

    #Increases counter for each row that sums to 10, meaning the line is completed
    count = 1
    for rowIndex in range(field.shape[0]):
        if np.sum(field[rowIndex]) == 10:
            field[rowIndex] = np.zeros(10)
            count += 1
    
    #Moves all rows down if they have space to do so
    for rowIndex in range(field.shape[0]):
        if np.sum(field[rowIndex]) == 0:
            for backwards in range(rowIndex, -1, -1):
                if backwards - 1 > 0:
                    field[backwards] = field[backwards - 1]
                else:
                    field[backwards] = np.zeros(10)

    #Returns an increasingly higher reward with lower heights and more completed lines
    #h -= 10
    if count > 1:
        return abs(h) ** count
    else:
        return 20 - h

def moveLeft(gameState, shape, times):

    yMin = 10
    yMax = 0

    #print(shape)

    #finding height of block
    for i in range(0, 4):

        if(shape[i][1] < yMin):
            
            yMin = shape[i][1]
        
        if(shape[i][1] > yMax):
            
            yMax = shape[i][1]   

    Y = yMax - yMin + 1

    #print(Y, yMax, yMin)

    leftMost = np.ones(Y, dtype= int)*10
    leftMostXY = np.ones((Y, 2), dtype = int)

    #finding left most blocks on each row
    for b in range(0, Y):
        
        for i in range (0,4):
            
            if(shape[i][1] == yMin + b and shape[i][0] < leftMost[b]):
                
                leftMost[b] = shape[i][0]
                
                leftMostXY[b][0] = shape[i][0]
                leftMostXY[b][1] = shape[i][1]

    clear = True
    bounds = True

    for e in range(0, times):

        #print(leftMostXY)

        for b in range(0,Y):
            
            if(leftMostXY[b][0]-1 < 0):
                
                bounds = False

        if(bounds == True):

            for b in range(0,Y):
                
                if(leftMostXY[b][0] > 0 and gameState[leftMostXY[b][1]][leftMostXY[b][0]-1] == 1):
                    

                    #print(leftMostXY[b][0] == True)
                    #print(gameState[leftMostXY[b][1]][leftMostXY[b][0]-1] == 1)

                    clear = False
                    #print("break")
            
            if(clear == True and bounds == True):
                
                for b in range(0,Y):
                  
                    leftMostXY[b][0] = leftMostXY[b][0] - 1

                for b in range(0,4):

                    gameState[shape[b][1]][shape[b][0]] = 0

                for b in range(0,4):

                    shape[b][0] = shape[b][0] - 1
                    gameState[shape[b][1]][shape[b][0]] = 1

    #print(gameState)

def moveRight(gameState, shape, times):

    yMin = 10
    yMax = 0

    #finding height of block
    for i in range(0, 4):

        if(shape[i][1] < yMin):
            
            yMin = shape[i][1]
        
        if(shape[i][1] > yMax):

            yMax = shape[i][1]   

    Y = yMax - yMin + 1

    #print(Y, yMax, yMin)
    #print("Y, yMax, yMin")
    #print(shape)
    #print("inputShape")


    rightMost = np.ones(Y, dtype= int)*-100000
    rightMostXY = np.ones((Y, 2), dtype = int)

    #finding right most blocks on each row
    for b in range(0, Y):
        
        for i in range (0,4):
            
            if(shape[i][1] == yMin + b and shape[i][0] > rightMost[b]):
                
                rightMost[b] = shape[i][0]

                rightMostXY[b][0] = shape[i][0]
                rightMostXY[b][1] = shape[i][1]
    
    #print(rightMostXY)
    #print("right most found")

    clear = True
    bounds = True

    for e in range(0, times):

        for b in range(0,Y):
            
            if(rightMostXY[b][0] + 1 > 9):
                
                #print(rightMostXY)
                #print("right boundry condition")
                bounds = False

            #else:

            #rightMostXY[b][0] = rightMostXY[b][0] + 1

        if(bounds == True):

            for b in range(0,Y):

                if(rightMostXY[b][0] < 9 and gameState[rightMostXY[b][1]][rightMostXY[b][0]+1] == 1):
                    
                    #print("rightMostXY[b][0] < 9 and gameState[rightMostXY[b][1]][rightMostXY[b][0]+1] == 1")
                    clear = False

            if(clear == True and bounds == True):

                for b in range(0,Y):

                    rightMostXY[b][0] = rightMostXY[b][0] + 1

                for b in range(0,4):

                    gameState[shape[b][1]][shape[b][0]] = 0

                for b in range(0,4):

                    shape[b][0] = shape[b][0] + 1
                    gameState[shape[b][1]][shape[b][0]] = 1
    
    #print(gameState)
    #print(rightMostXY)
    #print("right Most end")

def dropBlock(gameState, shape):

    #loop till the block colides?

    minX = 10
    maxX = 0

    for b in range(0,4):

        if(shape[b][0] < minX):

            minX = shape[b][0]
        
        if(shape[b][0] > maxX):

            maxX = shape[b][0]

    #print("min", minX)
    #print("max", maxX)

    X = 1 + maxX - minX

    #print(X)

    bottoms = np.ones(X,dtype=int)*-100000
    bottomBlocks = np.zeros((X, 2), dtype= int)


    for b in range(0, X):
        
        for i in range (0,4):
            
            if(shape[i][0] == minX + b and shape[i][1] >= bottoms[b]):
                
                #print("pew")

                bottoms[b] = shape[i][1]
                bottomBlocks[b][0] = shape[i][0]
                bottomBlocks[b][1] = shape[i][1]
    
    clear = True
    bounds = True

    #print(shape)
    #print("shape input")
    
    #print(bottomBlocks)

    #print(bottomBlocks)
    #print("Blocks Identified")


    for e in range(0, 19):

        for b in range(0,X):
            
            if(bottomBlocks[b][1]+1 > 19):
                
                #print("bottom block trigger")
                #print(bottomBlocks)
                bounds = False

        if(bounds == True):
            
            for b in range(0,X):    

                if(bottomBlocks[b][1] <= 19 and gameState[bottomBlocks[b][1]+1][bottomBlocks[b][0]] == 1 ):
                    

                    #print(bottomBlocks)
                    #print(bottomBlocks[b][1]+1,bottomBlocks[b][0])
                    #print("bottomBlocks[b][1] <= 19 and gameState[bottomBlocks[b][1]+1][bottomBlocks[b][0]] == 1 ")
                    clear = False
                    bounds = False

            if(clear == True and bounds == True):

                for b in range(0,X):
                    
                    bottomBlocks[b][1] += 1

                for b in range(0,4):

                    gameState[shape[b][1]][shape[b][0]] = 0

                for b in range(0,4):

                    shape[b][1] = shape[b][1] + 1
                    gameState[shape[b][1]][shape[b][0]] = 1

def StatePrime(blockID, gameState):

    gameStateSPrime = np.ones((4,20,10), dtype = int)*gameState
    blockXY = np.zeros((4, 4, 2), dtype = int)

    if(blockID == 0):

            #setting initial x, y for rotation 1
            blockXY[0][0][0] = 3
            blockXY[0][0][1] = 0
            
            blockXY[0][1][0] = 4
            blockXY[0][1][1] = 0
            
            blockXY[0][2][0] = 5
            blockXY[0][2][1] = 0
            
            blockXY[0][3][0] = 6
            blockXY[0][3][1] = 0

            gameStateSPrime[1][0][6] = 1  

            gameStateSPrime[1][0][5] = 1

            gameStateSPrime[1][0][4] = 1

            gameStateSPrime[1][0][2] = 1

            #checks if our rotation is valid
            if(gameStateSPrime[1][3][3] != 1 and gameStateSPrime[1][2][3] != 1 and gameStateSPrime[1][1][3] != 1):
                #rotate only 0 , 1

                #one rotation
                gameStateSPrime[1][3][3] = 1
                gameStateSPrime[1][0][6] = 0  

                gameStateSPrime[1][2][3] = 1
                gameStateSPrime[1][0][5] = 0

                gameStateSPrime[1][1][3] = 1
                gameStateSPrime[1][0][4] = 0
                
                gameStateSPrime[1][0][3] = 1
                gameStateSPrime[1][0][2] = 0

                blockXY[1][0][0] = 3
                blockXY[1][0][1] = 0
                
                blockXY[1][1][0] = 3
                blockXY[1][1][1] = 1
                
                blockXY[1][2][0] = 3
                blockXY[1][2][1] = 2
                
                blockXY[1][3][0] = 3
                blockXY[1][3][1] = 3



    elif(blockID == 1):

        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 0

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 0
        
        blockXY[0][2][0] = 4
        blockXY[0][2][1] = 1

        blockXY[0][3][0] = 5
        blockXY[0][3][1] = 1

        if(gameStateSPrime[1][1][3] != 1 and gameStateSPrime[1][2][3] != 1):

            #do the rotatio 
            blockXY[1][0][0] = 4
            blockXY[1][0][1] = 0

            blockXY[1][1][0] = 4
            blockXY[1][1][1] = 1
            
            blockXY[1][2][0] = 3
            blockXY[1][2][1] = 1

            blockXY[1][3][0] = 3
            blockXY[1][3][1] = 2

            for r in range (0,2):

                for b in range(0,4):

                    #gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

        #print(blockID)
        #print(board)

    elif(blockID == 5):

        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 1

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 1
        
        blockXY[0][2][0] = 4
        blockXY[0][2][1] = 0

        blockXY[0][3][0] = 5
        blockXY[0][3][1] = 0

        if(gameStateSPrime[1][1][5] != 1 and gameStateSPrime[1][2][5] != 1):

            #do the rotatio 
            blockXY[1][0][0] = 3
            blockXY[1][0][1] = 1

            blockXY[1][1][0] = 3
            blockXY[1][1][1] = 0
            
            blockXY[1][2][0] = 4
            blockXY[1][2][1] = 2

            blockXY[1][3][0] = 4
            blockXY[1][3][1] = 1

            for r in range (0,2):

                for b in range(0,4):

                    gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

            #print(gameStateSPrime[1])
            #print('\n')
            #print(gameStateSPrime[0])

        #S block
        #print(blockID)

    elif(blockID == 2):

        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 0

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 0
    
        blockXY[0][2][0] = 5
        blockXY[0][2][1] = 0

        blockXY[0][3][0] = 4
        blockXY[0][3][1] = 1

        if(gameStateSPrime[1][2][4] != 1 and gameStateSPrime[1][1][5] != 1):
            #right pointing
            blockXY[1][0][0] = 4
            blockXY[1][0][1] = 2

            blockXY[1][1][0] = 4
            blockXY[1][1][1] = 1

            blockXY[1][2][0] = 4
            blockXY[1][2][1] = 0

            blockXY[1][3][0] = 5
            blockXY[1][3][1] = 1

            if(gameStateSPrime[2][1][3] != 1):
                #up pointing
                blockXY[2][0][0] = 5
                blockXY[2][0][1] = 1

                blockXY[2][1][0] = 4
                blockXY[2][1][1] = 1

                blockXY[2][2][0] = 3
                blockXY[2][2][1] = 1

                blockXY[2][3][0] = 4
                blockXY[2][3][1] = 0

                if(gameStateSPrime[3][2][4] != 1): 
                    #left pointing
                    blockXY[3][0][0] = 4
                    blockXY[3][0][1] = 0

                    blockXY[3][1][0] = 4
                    blockXY[3][1][1] = 1

                    blockXY[3][2][0] = 4
                    blockXY[3][2][1] = 2

                    blockXY[3][3][0] = 3
                    blockXY[3][3][1] = 1

        for r in range(0,4):

            for b in range(0,4):
                    
                    gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    

            for b in range(0,4):

                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

        #print(gameStateSPrime[:])

        #t block 4 rotations
        #print(blockID)

    elif(blockID == 3):

        
        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 0

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 0
    
        blockXY[0][2][0] = 5
        blockXY[0][2][1] = 0

        blockXY[0][3][0] = 3
        blockXY[0][3][1] = 1

        if(gameStateSPrime[1][2][5] != 1 and gameStateSPrime[1][1][5] != 1):
            #right pointing
            blockXY[1][0][0] = 5
            blockXY[1][0][1] = 2

            blockXY[1][1][0] = 4
            blockXY[1][1][1] = 1

            blockXY[1][2][0] = 4
            blockXY[1][2][1] = 0
    
            blockXY[1][3][0] = 4
            blockXY[1][3][1] = 2

            #up pointing
            blockXY[2][0][0] = 5
            blockXY[2][0][1] = 1

            blockXY[2][1][0] = 4
            blockXY[2][1][1] = 1

            blockXY[2][2][0] = 3
            blockXY[2][2][1] = 1

            blockXY[2][3][0] = 5
            blockXY[2][3][1] = 0

            if(gameStateSPrime[0][2][4] != 1): 
                #left pointing
                blockXY[3][0][0] = 4
                blockXY[3][0][1] = 0

                blockXY[3][1][0] = 4
                blockXY[3][1][1] = 1

                blockXY[3][2][0] = 4
                blockXY[3][2][1] = 2

                blockXY[3][3][0] = 3
                blockXY[3][3][1] = 0

        for r in range(0,4):

            for b in range(0,4):
                    
                    gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    

            for b in range(0,4):

                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

        #print(gameStateSPrime[:])

        #L block
        #print(blockID)

    elif(blockID == 4 ):
        
        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 0

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 0
    
        blockXY[0][2][0] = 5
        blockXY[0][2][1] = 0

        blockXY[0][3][0] = 5
        blockXY[0][3][1] = 1

        if(gameStateSPrime[1][2][3] != 1 and gameStateSPrime[1][1][3] != 1):
            #right pointing
            blockXY[1][0][0] = 4
            blockXY[1][0][1] = 2

            blockXY[1][1][0] = 4
            blockXY[1][1][1] = 1

            blockXY[1][2][0] = 4
            blockXY[1][2][1] = 0

            blockXY[1][3][0] = 5
            blockXY[1][3][1] = 0

            #up pointing
            blockXY[2][0][0] = 5
            blockXY[2][0][1] = 1

            blockXY[2][1][0] = 4
            blockXY[2][1][1] = 1

            blockXY[2][2][0] = 3
            blockXY[2][2][1] = 1

            blockXY[2][3][0] = 3
            blockXY[2][3][1] = 0

            if(gameStateSPrime[0][2][4] != 1): 
                #left pointing
                blockXY[3][0][0] = 4
                blockXY[3][0][1] = 0

                blockXY[3][1][0] = 4
                blockXY[3][1][1] = 1

                blockXY[3][2][0] = 4
                blockXY[3][2][1] = 2

                blockXY[3][3][0] = 3
                blockXY[3][3][1] = 2

        for r in range(0,4):

            for b in range(0,4):
                    
                    gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    

            for b in range(0,4):

                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

        #print(gameStateSPrime[:])

        #inv L block
        #print(blockID)

    elif(blockID == 6):

        #square

        blockXY[0][0][0] = 3
        blockXY[0][0][1] = 0

        blockXY[0][1][0] = 4
        blockXY[0][1][1] = 0

        blockXY[0][2][0] = 3
        blockXY[0][2][1] = 1

        blockXY[0][3][0] = 4
        blockXY[0][3][1] = 1

        for r in range(0,1):

            for b in range(0,4):
                    
                    gameStateSPrime[r][blockXY[0][b][1]][blockXY[0][b][0]] = 0
                    

            for b in range(0,4):

                    gameStateSPrime[r][blockXY[r][b][1]][blockXY[r][b][0]] = 1

        #print(blockXY[0])

        #print(blockID)

    return blockXY, gameStateSPrime

def virtualExecute(field, rotCoordinates, pos):

    t = 0
    #print("The butt has been chosen")
    #Moves the block into the appropriate position in the virtual game space
    if(pos < 3):

        t = 3 - pos
        #print
        moveLeft(field, rotCoordinates, int(t))
        #print
        dropBlock(field, rotCoordinates)
        #print

    if(pos >= 3):
        #3>2
        t = pos - 3

        moveRight(field, rotCoordinates, int(t))
        dropBlock(field, rotCoordinates)

    return field