# Tint-Deep-Q-Ai

Author: 	John Bowersox

Date:		12/10/2019

Title: 		Tint Deep Q Ai

This is a final project for my graduate course in applied machine learning and ai, where I worked with a 
partner to build a deep q learning Ai for Tint a tetris game in a linux environment.  We decided to use a 
convolutional neural network to attempt to approximate the bellman equation for decision making. The 
system works by taking screen shots of linux virtual machine, then using some basic image 
preprocessing, to shrink and clean input data, for faster processing in the neural net. After researching 
professional play, a heuristic was chosen for how commands were executed, rotate and drop. This 
greatly reduced the unexpectedly massive hypothesis space in a time sensitive application. 

Basic Ai workflow
1.	Wait for the current and future block to spawn and take a screen shot.
2.	Image process and identify the blocks with boolean logic.
3.	Generate four copies of the game state, and rotate the movable block in the game state.
4.	Run each current rotational state through the neural net for an action output, which is the 
highest predicted score.
5.	Generate four copies for each resultant state in memory, each with a different future block 
rotation. This makes a total of up to 16 combinations.
6.	Run each of the future rotational states through the neural net, and find the Maximal 
combination of current and future action, this action is executed and a real score is 
generated, there is a small chance that decreases that a random chance of exploration is 
instead chosen.
7.	Relevant information is then stored into recall memory for training.
8.	The system then executes it in the actual game state, and waits to receive an updated game 
state.
9.	The process loops till a terminal state is reached, then recall training proceeds, which is one 
complete round of training for the AI.
