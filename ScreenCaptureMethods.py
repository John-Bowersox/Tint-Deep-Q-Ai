#new stuff
from Xlib import display, X
import PIL.Image as Image
import time
import datetime
import pyautogui as pag
import numpy as np
import cv2

#Rotation amounts associated with each piece ID
rots = np.array([2,2,4,4,4,2,1])

def newPieceCheck(firstBlock):
    W,H = 72, 54
    dsp = display.Display()
    root = dsp.screen().root

    if firstBlock:
        top = 357
    else:
        top = 339

    raw = root.get_image(473,top, W,H, X.ZPixmap, 0xffffffff)
    image = Image.frombytes("RGB", (W,H), raw.data, "raw", "BGRX")
    screen =  np.array(image)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(screen_gray, 53,255, cv2.THRESH_BINARY)

    height, width = thresh.shape
    mid = thresh[9:height:18]
    mid = mid.T
    mid = mid[9:width:18]
    mid = mid.T

    np.place(mid, mid>0, 1)
    return np.sum(mid) > 3, mid

def newPieceID(mid):
    #Index || Piece
    # 0 = Long [[0,0,0,0], [1,1,1,1], [0,0,0,0]] Unique Point: (1,3)
    # 1 = Z [[1,1,0,0], [0,1,1,0], [0,0,0,0]] Unique Point: (1,2), NOT(1,3)
    # 2 = T [[0,0,0,0], [1,1,1,0], [0,1,0,0]] Unique Point: (2,1)
    # 3 = L [[0,0,0,0], [1,1,1,0], [1,0,0,0]] Unique Point: (2,0)
    # 4 = J [[0,0,0,0], [1,1,1,0], [0,0,1,0]] Unique Point: (2,2)
    # 5 = S [[0,1,1,0], [1,1,0,0], [0,0,0,0]] Unique Point: (0,2)
    # 6 = Square [[1,1,0,0], [1,1,0,0], [0,0,0,0]] Unique Point: (0,0), (1,0)
    
    #print("THis is the new piece \n", mid)

    #O = Long
    if bool(mid[1][3]):
        return 0, rots[0]
    
    #1 = Z
    if bool(mid[1][2]) and not bool(mid[1][0]):
        return 1, rots[1]

    #2 = T
    if bool(mid[2][1]):
        return 2, rots[2]

    #3 = L
    if bool(mid[2][0]):
        return 3, rots[3]

    #4 = J
    if bool(mid[2][2]):
        return 4, rots[4]

    #5 = S
    if bool(mid[0][2]):
        return 5, rots[5]
    
    #6 = Square
    if bool(mid[0][0]) and bool(mid[1][0]):
        return 6, rots[6]
        
#Takes a screenshot and returns a boolean nparray representing the game field
def screenCap():
    W,H = 180, 360
    dsp = display.Display()
    root = dsp.screen().root
    raw = root.get_image(419,339, W,H, X.ZPixmap, 0xffffffff)
    image = Image.frombytes("RGB", (W,H), raw.data, "raw", "BGRX")
    screen =  np.array(image)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(screen_gray, 53,255, cv2.THRESH_BINARY)

    height, width = thresh.shape
    mid = thresh[9:height:18]
    mid = mid.T
    mid = mid[9:width:18]
    mid = mid.T

    np.place(mid, mid>0, 1)
    return mid


#Sees if the game has ended in the terminal, true if so
def resetCheck():
    W,H = 1, 1
    dsp = display.Display()
    root = dsp.screen().root
    raw = root.get_image(300,700, W,H, X.ZPixmap, 0xffffffff)
    image = Image.frombytes("RGB", (W,H), raw.data, "raw", "BGRX")
    screen =  np.array(image)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    #print(screen_gray)
    ret, thresh = cv2.threshold(screen_gray, 24,255, cv2.THRESH_BINARY)

    return not thresh[0][0] > 0

#Identifies the next piece that will serve as action prime
def previewCap():

    W,H = 72, 36
    dsp = display.Display()
    root = dsp.screen().root
    raw = root.get_image(77,692, W,H, X.ZPixmap, 0xffffffff)
    screen = Image.frombytes("RGB", (W,H), raw.data, "raw", "BGRX")

    # Args 1 and 3 are start and end X respectively starting from left hand of screen
    # Args 2 and 4 are start and end Y respecitveky starting from top
    screen =  np.array(screen)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(screen_gray, 53,255, cv2.THRESH_BINARY)
    fileName = "screencapTest_" + "size4"+ ".jpg"
    #cv2.imwrite(fileName, screen)
    #cv2.imshow('window', screen)

    height, width = thresh.shape
    mid = thresh[5:height:18]
    mid = mid.T
    mid = mid[5:width:9]
    mid = mid.T

    np.place(mid, mid>0, 1)
    np.set_printoptions(threshold=np.inf)
    
    #The next piece can be identified based on which of the following np.arrays it matches

    #Index || Piece
    # 0 = Long [[1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0]]
    # 1 = Z [[0,1,1,1,1,0,0,0], [0,0,0,1,1,1,1,0]]
    # 2 = T [[0,1,1,1,1,1,1,0], [0,0,0,1,1,0,0,0]]
    # 3 = L [[0,1,1,1,1,1,1,0], [0,1,1,0,0,0,0,0]]
    # 4 = J [[0,1,1,1,1,1,1,0], [0,0,0,0,0,1,1,0]]
    # 5 = S [[0,0,0,1,1,1,1,0], [0,1,1,1,1,0,0,0]]
    # 6 = Square [[0,0,1,1,1,1,0,0], [0,0,1,1,1,1,0,0]]

    keys = np.array([[[1,1,1,1,1,1,1,1], [0,0,0,0,0,0,0,0]], [[0,1,1,1,1,0,0,0], [0,0,0,1,1,1,1,0]], [[0,1,1,1,1,1,1,0], [0,0,0,1,1,0,0,0]], [[0,1,1,1,1,1,1,0], [0,1,1,0,0,0,0,0]], [[0,1,1,1,1,1,1,0], [0,0,0,0,0,1,1,0]], [[0,0,0,1,1,1,1,0], [0,1,1,1,1,0,0,0]], [[0,0,1,1,1,1,0,0], [0,0,1,1,1,1,0,0]]])

    #Finds the correct ID of the piece and its number of rotations
    rightIndex = -1
    for index in range(keys.shape[0]):
        if np.array_equal(keys[index], mid):
            rightIndex = index
            break

    return rightIndex, rots[rightIndex]