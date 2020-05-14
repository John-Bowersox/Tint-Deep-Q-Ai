import pyautogui as pag
import time

#Starts a tetris game from the base terminal
def startGame():
    pag.typewrite("tint")
    pag.press("enter")
    pag.press("1")
    pag.press("enter")
    time.sleep(0.5)
    pag.press("s")
    time.sleep(0.05)
    pag.press("p")

#Rotates the piece, then moves it into position and drops it
def order66(pos, rot):
    pos = int(pos)
    #pag.click(100,700)

    #Unpauses the game to execute the move physically
    pag.press("p")
    time.sleep(0.1)
    start = 3
    #print("Rotations, ", rot)
    #Rotates the piece the designated number of times
    for i in range (rot):
        #print("Rotating " ,i)
        pag.press("k")
        time.sleep(0.01)

    #Moves the piece into position
    if pos > start:  
        for i in range(pos - start):
            pag.press("right")
            time.sleep(0.01)

    else:
        for i in range(start - pos):   
            pag.press("left")
            time.sleep(0.01)

    #Drops the piece
    pag.press("down")

    return 0
