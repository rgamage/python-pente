#/usr/bin/python
#Pente Game, using Object-Oriented programming techniques
#Randy Gamage
#9-AUG-2005

#Design Notes:
#There are four main classes, to separate the tasks roughly along the Model, View, Control type
#of design pattern.  The classes are as follows:
# Matrix - A generic matrix object to store and manipulate a two-dimensional array
# PenteModel - The mathematical model that performs analysis/statistics of the pente game
# PenteView - The GUI for the game.  Implemented here using PyGame, but could use any GUI framework
# PenteGame - The game state variables, that keeps track of players and who is winning, etc.
# PenteAI - The Artificial Intelligence class that allows the computer to calculate moves and compete against another player

#These constants are all related to the View, but for now we'll make them globals,
#just because it's easier and makes for cleaner looking code. Eventually these should
#be global only within the View module, but for now all classes are in the same file.

#Deployment notes:
#Successfully used py2exe to build this script into a windows .exe file.
#It seems to work, even with psyco enabled.
#Next task, use Inno Setup and IStool to create a windows installer for it.
# www.istool.org
# www.innosetup.com

#Version Tracking
# Current Major Version = 0
# Major Version 0:
# First major version, initial release through test phases
# Current Minor Version = 1
# Minor Version 1:
# First minor version, still fixing bugs and modifying appearance. No windows gui 'widgets',
# just graphical display (game board and status line).
# Current Build:
# The Build number is kept in the file pente.cfg.  The build script, build.py, increments
# this value at every build, and stores an archive of the source code in the archive folder.
# The file name of the archive is "pente_<full version>.py  The full version
# number is Major+"."+Minor+"."+Build

# import necessary modules
import pygame
from random import randint
from pygame.locals import *
import copy

# debug switch
DEBUG = False
#DEBUG = True
if DEBUG:
    import os
    os.chdir("D:\\gamoto\\python\\pente\\dist")
    print "current dir = %s" % (os.getcwd())
else:
    import psyco
    psyco.full()
    
# define color constants
BLACK = pygame.color.Color('black')
WHITE = pygame.color.Color('white')
RED = pygame.color.Color('red')
BLUE = pygame.color.Color('blue')
LTGREEN = 88,143,11
LTBLUE = 49,92,168
BACKCOLOR = 204,153,51
HIGHLIGHT = 255,204,102
SHADOW = 153,102,0
PCOLORS = [LTBLUE,LTGREEN] #player colors
#define other visual constants
SIZE=13
BOARDSIZE=400
HUMAN=0     #human is player 1
COMPUTER=1  #computer is player 2
LINEWIDTH=2
CELLSIZE = BOARDSIZE/(SIZE-1)
BMARGIN=50  #bottom margin
LMARGIN=50  #left margin
RMARGIN=50  #right margin
TMARGIN=20   #top margin
STATUSHEIGHT = 35  #height of status line at bottom
    
class Matrix:
    """A generic matrix object to store and manipulate a square two-dimensional array.
    Constructor takes two arguments: size, filler.  Size is the size of the array,
    and filler is what to fill it with upon creation.
    Note that this matrix uses [row][col] notation, but also maintains x & y indices,
    so matrix[r][c] = matrix[y][x].  When iterating, these indices are updated, allowing
    you to know 'where you are' during an iteration loop."""
    def __init__(self,msize,filler):
        #create matrix filled with filler values
        self.matrix = [[filler for i in range(msize)] for j in range(msize)]
        #initialize state variables
        self.x=self.col=0  #current x location of iterator within the array
        self.y=self.row=0  #current y location of iterator within the array
        self.size = msize
    def __iter__(self):
        self.y=self.row = 0
        for row in self.matrix:
            self.x=self.col=0
            for cell in row:
                yield cell
                self.col += 1
                self.x += 1
            self.row += 1
            self.y += 1
    def Clear(self):
        #Clear all cells in the matrix
        for x in range(self.size):
            for y in range(self.size):
                self.matrix[x][y]=0
    def CheckRight(self,n,v):
        #Given number of cells n and value v, checks if cells to the right of current position are occupied (including current position)
        if (self.size-self.col<n):
            return False #not enough room to right
        for i in range(0,n):
            if self.matrix[self.row][self.col+i] <> v:
                return False
        return True
    def CheckDown(self,n,v):
        #Given number of cells n and value v, checks if cells down from current position are occupied (including current position)
        if (self.size-self.row<n):
            return False  #not enough room below
        for i in range(0,n):
            if self.matrix[self.row+i][self.col] <> v:
                return False
        return True
    def CheckDiag1(self,n,v):
        #Given number of cells n and value v, checks if cells diag down from current position are occupied (including current position)
        if (self.size-self.row<n or self.size-self.col<n):
            return False  #not enough room down or to right
        for i in range(0,n):
            if self.matrix[self.row+i][self.col+i] <> v:
                return False
        return True
    def CheckDiag2(self,n,v):
        #Given number of cells n and value v, checks if cells diag up from current position are occupied (including current position)
        if self.size-self.col<n or self.row<n-1:
            return False  #not enough room up or right
        for i in range(0,n):
            if self.matrix[self.row-i][self.col+i] <> v:
                return False
        return True
    
class PenteModel:
    def __init__(self,size,numplayers=2):
        self.MAXRUN = 5
        self.MAXCAPTURES = 5
        # create a game grid
        self.M = Matrix(size,0)  #grid that holds pieces on board
        self.size = size
        self.NumPlayers = numplayers
        self.wins = [0,0]
        self.Reset()

    def Reset(self):
        # Reset game state to a new game
        self.Turn = HUMAN   # track whose turn it is; HUMAN goes first
        self.Winner = None
        self.Captures=[0,0]  #captures for P1,P2
        self.lastmove = int(self.size/2),int(self.size/2)
        self.M.Clear()
        # data structures to count pairs, triplets, etc is as follows:
        # Runs[] holds list of arrays, each containing another list of runs of each size
        # Runs[0] holds runlist for first player
        # Runs[1] holds runlist for second player
        # Runs[0][0]=0
        # Runs[0][1]=player 1 list of coordinates of single pieces
        # Runs[0][2]=player 1 list of coordinates of pairs
        # Runs[0][3]=player 1 list of coordinates of triplets
        # Runs[0][4]=player 1 list of coordinates of quadruplets
        # Runs[0][5]=player 1 list of coordinates of pentuplets (gamewinners)
        # initialize run lists
        self.Runs = [ [0,[],[],[],[],[]],  # player 1 runlist
                      [0,[],[],[],[],[]] ] # player 2 runlist
        
    def TakeTurn(self,row,col):
        # make sure no one's used this space
        if self.M.matrix[row][col]<>0:
            # this space is in use
            return

        # place piece in model
        self.PlacePiece(row,col,self.Turn)
        
        # check if this is a capture
        if self.CheckCaptures(row,col,self.Turn):
            if self.Turn == COMPUTER:
                laugh.play()
            else:
                ohhh.play()
                
        #remember this was the most recent move
        self.lastmove = row,col

        if DEBUG:
          if self.Turn == COMPUTER:
            print "\nComputer moves to %d,%d" % (row,col)
          else:
            print "\nYou moved to %d,%d" % (row,col)

        # toggle Turn to the next player's move
        self.Turn = (self.Turn + 1) % self.NumPlayers

    def gameWon(self):
        # determine if anyone has won the game
        # ---------------------------------------------------------------
        for p in range(self.NumPlayers):
           if len(self.Runs[p][self.MAXRUN])>0 or self.Captures[p]==self.MAXCAPTURES:
              self.Winner=p

    def PlacePiece(self,row,col,p):
        # place a piece in the matrix, mark the space as used
        self.M.matrix[row][col] = p+1
        
    def CountRuns(self,p,n,runs):
        #count how many runs of n, of piece p are on the board, for each player
        #Store them in a list of lists global runs[]
        #first define functions to check runs in each direction
        def Nested(run):
            #check if a run is already nested inside a larger run
            n=len(run)
            for ni in range(n+1,self.MAXRUN+1):
                for runlist in runs[ni]:
                    for coord in run:
                        if not coord in runlist:
                            return False
                    return True
            return False
        
        runs[n]=[]
        for cell in self.M:
            if n==1 and cell==p:  #single piece
                run = [(self.M.row,self.M.col)]
                if not Nested(run):
                    runs[n].append(run)
                break
            if self.M.CheckRight(n,p):
                run = [(self.M.row,self.M.col+i) for i in range(n)]
                if not Nested(run):
                    runs[n].append(run)
            if self.M.CheckDown(n,p):
                run = [(self.M.row+i,self.M.col) for i in range(n)]
                if not Nested(run):
                    runs[n].append(run)
            if self.M.CheckDiag1(n,p):
                run = [(self.M.row+i,self.M.col+i) for i in range(n)]
                if not Nested(run):
                    runs[n].append(run)
            if self.M.CheckDiag2(n,p):
                run = [(self.M.row-i,self.M.col+i) for i in range(n)]
                if not Nested(run):
                    runs[n].append(run)
        return len(runs[n])

    def PickCells(self,m,n):
        #returns coordinates of cells in matrix m, with value of n
        result=[]
        for cell in m:
            if cell==n:
                result.append((m.row,m.col))
        return result

    def GetEnds(self,n,run):
        #given a run of length 2-5, returns a list of coords (2, 1 at each end) of the
        #cells next in each direction. If next cell is off board, don't include that in the list
        result=[]
        ROW=0    #index positions. Row first,
        COL=1    #then Column
        START=0  #Starting coordinate point
        END=n-1  #Ending coordinate point
        if run[START][COL]==run[START+1][COL]:
            #vertical run
            if run[START][ROW]>0:
                result.append((run[START][ROW]-1,run[START][COL]))
            if run[END][ROW]<self.size-1:
                result.append((run[END][ROW]+1,run[START][COL]))
        if run[START][ROW]==run[START+1][ROW]:
            #horizontal run
            if run[START][COL]>0:
                result.append((run[START][ROW],run[START][COL]-1))
            if run[END][COL]<self.size-1:
                result.append((run[START][ROW],run[END][COL]+1))
        if run[START][ROW]+1==run[START+1][ROW] and run[START][COL]+1==run[START+1][COL]:
            #diagonal down-right run
            if run[START][ROW]>0 and run[START][COL]>0:
                result.append((run[START][ROW]-1,run[START][COL]-1))
            if run[END][ROW]<self.size-1 and run[END][COL]<self.size-1:
                result.append((run[END][ROW]+1,run[END][COL]+1))
        if run[START][COL]+1==run[START+1][COL] and run[START][ROW]-1==run[START+1][ROW]:
            #diagonal up-right run
            if run[END][ROW]>0 and run[END][COL]<self.size-1:
                result.append((run[END][ROW]-1,run[END][COL]+1))
            if run[START][COL]>0 and run[START][ROW]<self.size-1:
                result.append((run[START][ROW]+1,run[START][COL]-1))
        return result

    def GetOpenEnds(self,n,run):
        #given a run of length 2-5, returns a list of coords (2, 1 at each end) of the
        #cells next in each direction. If next cell is off board, don't include that in the list
        #Same as GetEnds, BUT:
        #If next cell is occupied by a game piece, don't include it in the list
        ROW=0    #index positions. Row first,
        COL=1    #then Column
        START=0  #Starting coordinate point
        END=n-1  #Ending coordinate point
        result=[]
        if run[START][COL]==run[START+1][COL]:
            #vertical run
            if run[START][ROW]>0:
                if self.M.matrix[run[START][ROW]-1][run[START][COL]]==0:
                    result.append((run[START][ROW]-1,run[START][COL]))
            if run[END][ROW]<self.size-1:
                if self.M.matrix[run[END][ROW]+1][run[START][COL]]==0:
                    result.append((run[END][ROW]+1,run[START][COL]))
        if run[START][ROW]==run[START+1][ROW]:
            #horizontal run
            if run[START][COL]>0:
                if self.M.matrix[run[START][ROW]][run[START][COL]-1]==0:
                   result.append((run[START][ROW],run[START][COL]-1))
            if run[END][COL]<self.size-1:
                if self.M.matrix[run[START][ROW]][run[END][COL]+1]==0:
                   result.append((run[START][ROW],run[END][COL]+1))
        if run[START][ROW]+1==run[START+1][ROW] and run[START][COL]+1==run[1][1]:
            #diagonal down-right run
            if run[START][ROW]>0 and run[START][COL]>0:
                if self.M.matrix[run[START][ROW]-1][run[START][COL]-1]==0:
                   result.append((run[START][ROW]-1,run[START][COL]-1))
            if run[END][ROW]<self.size-1 and run[END][COL]<self.size-1:
                if self.M.matrix[run[END][ROW]+1][run[END][COL]+1]==0:
                   result.append((run[END][ROW]+1,run[END][COL]+1))
        if run[START][ROW]-1==run[START+1][ROW] and run[START][COL]+1==run[START+1][COL]:
            #diagonal up-right run
            if run[END][ROW]>0 and run[END][COL]<self.size-1:
                if self.M.matrix[run[END][ROW]-1][run[END][COL]+1]==0:
                   result.append((run[END][ROW]-1,run[END][COL]+1))
            if run[START][COL]>0 and run[START][ROW]<self.size-1:
                if self.M.matrix[run[START][ROW]+1][run[START][COL]-1]==0:
                   result.append((run[START][ROW]+1,run[START][COL]-1))
        if run[START][ROW]+1==run[START+1][ROW] and run[START][COL]-1==run[START+1][COL]:
            #diagonal down-left run
            if run[END][ROW]<self.size-1 and run[END][COL]>0:
                if self.M.matrix[run[END][ROW]+1][run[END][COL]-1]==0:
                   result.append((run[END][ROW]+1,run[END][COL]-1))
            if run[START][COL]<self.size-1 and run[START][ROW]>0:
                if self.M.matrix[run[START][ROW]-1][run[START][COL]+1]==0:
                   result.append((run[START][ROW]-1,run[START][COL]+1))
        return result

    def CheckCaptures(self,row,col,p):
        #check if any captures have occurred by placing a piece at row,col for given player p
        #note: the piece just placed must be one of the outer pieces (the one doing the capture)
        #because you capture yourself by moving between two pieces
        for run in self.Runs[(p+1)%self.NumPlayers][2]:
            endlist = self.GetEnds(2,run)
            if len(endlist)==2: #make sure the pair is in the open, not at the edge of the board
              if self.M.matrix[endlist[0][0]][endlist[0][1]]==p+1 and self.M.matrix[endlist[1][0]][endlist[1][1]]==p+1:
                if (row,col) in endlist: #this move must be one of the end cells
                    for cell in run:
                        #TO DO: Add operator overload to matrix, to allow this syntax:
                        # self.M(cell) = 0
                        self.M.matrix[cell[0]][cell[1]]=0  #remove pieces
                    self.Captures[p] += 1
                    return True
        return False

    def CalcStats(self):
       for p in range(self.NumPlayers):
         for i in range(self.MAXRUN,0,-1):
           self.CountRuns(p+1,i,self.Runs[p])

class PenteView:
    #Pente View Class, takes Model m and Board size as inputs
    def __init__(self,m,size):
        self.boardsize = size
        self.model = m
        self.ttt = pygame.display.set_mode ((self.boardsize+LMARGIN+RMARGIN,self.boardsize+TMARGIN+BMARGIN))
        pygame.display.set_caption ('Pente')
        #TO DO: add icon to window frame
#        gxicon = pygame.image.load('gamatronix.ico')
#        pygame.display.set_icon(gxicon)
        # create the game board
        self.board = self.initBoard (self.ttt)

    # declare our support functions
    def drawsquare(self,x,y,size,s):
        #draws a square of given size, with upper left corner at x,y coordinates, onto surface s
        pygame.draw.line(s,HIGHLIGHT,(x+1,y+1),(x+size-1,y+1),LINEWIDTH)
        pygame.draw.line(s,HIGHLIGHT,(x+1,y+1),(x+1,y+size-1),LINEWIDTH)
        pygame.draw.line(s,SHADOW,(x+size-1,y+1),(x+size-1,y+size-1),LINEWIDTH)
        pygame.draw.line(s,SHADOW,(x+1,y+size-1),(x+size-1,y+size-1),LINEWIDTH)

    def DrawSquares(self,s):
        # draw the squares on surface s
        for y in range(self.model.size-1):
            for x in range(self.model.size-1):
                self.drawsquare(x*CELLSIZE+LMARGIN,y*CELLSIZE+TMARGIN,CELLSIZE,s)

    def DrawCaptures(self,s,captures):
        # draw captured pair in margins
        r = int(LMARGIN/4.7)
        PLAYER1 = 0
        PLAYER2 = 1
        for i in range(captures[PLAYER1]):
            pygame.draw.circle(s,PCOLORS[PLAYER2],(5+r,int(5+TMARGIN+i*2.3*r+r)),r,0)
            pygame.draw.circle(s,PCOLORS[PLAYER2],(int(5+r+2.1*r),int(5+TMARGIN+i*2.3*r+r)),r,0)
        for i in range(captures[PLAYER2]):
            pygame.draw.circle(s,PCOLORS[PLAYER1],(5+r+LMARGIN+BOARDSIZE,int(5+TMARGIN+i*2.3*r+r)),r,0)
            pygame.draw.circle(s,PCOLORS[PLAYER1],(int(5+r+2.1*r+LMARGIN+BOARDSIZE),int(5+TMARGIN+i*2.3*r+r)),r,0)

        #Draw hash marks to keep track of wins
        MARKHEIGHT = 25
        MARKXSPACING = 7
        MARKYSPACING = 40
        MARKXOFFSET = 10
        MARKYOFFSET = TMARGIN+BOARDSIZE-10
        MARKWIDTH = 2
        for p in range(0,self.model.NumPlayers):
            for i in range(self.model.wins[p]):
               startx = MARKXOFFSET + p*(LMARGIN+BOARDSIZE) + MARKXSPACING * (i % 5)
               starty = MARKYOFFSET - int(i/5)*MARKYSPACING
               endx = startx
               endy = starty - MARKHEIGHT
               pygame.draw.line(s,BLACK,(startx,starty),(endx,endy),MARKWIDTH)
               if (i%5 == 4):
                   startx = MARKXOFFSET + p*(LMARGIN+BOARDSIZE) - 3
                   starty = MARKYOFFSET - int(i/5)*MARKYSPACING
                   endx = startx + 4*MARKXSPACING + 6
                   endy = starty - MARKHEIGHT
                   pygame.draw.line(s,BLACK,(startx,starty),(endx,endy),MARKWIDTH)
    
    def initBoard(self,ttt):
        # initialize the board and return it as a variable
        # ---------------------------------------------------------------
        # ttt : a properly initialized pyGame display variable

        # set up the background surface
        background = pygame.Surface (ttt.get_size())
        background = background.convert()
        background.fill (BACKCOLOR)

        # draw the squares
        self.DrawSquares(background)
        # return the board (surface)
        return background

    def drawStatus (self,board,turn,winner):
        # draw the status (i.e., player turn, etc) at the bottom of the board
        # ---------------------------------------------------------------
        # board : the initialized game board surface where the status will
        #         be drawn

        # determine the status message
        if (winner is None):
            if turn==COMPUTER:
               message = "My Turn... I'm thinking"
            else:
                message = "Your Turn"
        else:
            if winner==COMPUTER:
                message = "Sorry, I won!  - Click board to start again"
            else:
                message = "Congratulations, you won!  - Click board to start again"
        
        # render the status message
        #font = pygame.font.Font(None, 24)
        font = pygame.font.SysFont("Arial",24)
        text = font.render(message, 1, BLACK)

        # copy the rendered message onto the board
        board.fill (WHITE, (0, BOARDSIZE+TMARGIN+BMARGIN-STATUSHEIGHT, BOARDSIZE+LMARGIN+RMARGIN, STATUSHEIGHT))
        board.blit(text, (10, BOARDSIZE+TMARGIN+BMARGIN-STATUSHEIGHT))

    def showBoard (self,ttt, board,turn,winner):
        # redraw the game board on the display
        # ---------------------------------------------------------------
        # ttt   : the initialized pyGame display
        # board : the game board surface

        self.drawStatus (board,turn,winner)
        ttt.blit (board, (0, 0))
        pygame.display.flip()

    def boardPos (self,mouseX, mouseY):
        # given a set of coordinates from the mouse, determine which board space
        # (row, column) the user clicked in.
        # ---------------------------------------------------------------
        # mouseX : the X coordinate the user clicked
        # mouseY : the Y coordinate the user clicked

        # determine the row the user clicked
        row = (mouseY-TMARGIN+CELLSIZE/2) / CELLSIZE

        # determine the column the user clicked
        col = (mouseX-LMARGIN+CELLSIZE/2) / CELLSIZE
    
        # return the tuple containg the row & column
        return (row,col)

    def drawMove (self,board, boardRow, boardCol, p):
        # draw a Piece on the board in boardRow, boardCol
        # ---------------------------------------------------------------
        # board     : the game board surface
        # boardRow,
        # boardCol  : the Row & Col in which to draw the piece (0 based)
        # p     : Player (0 or 1)
    
        # determine the center of the square
        centerX = ((boardCol) * CELLSIZE) +LMARGIN
        centerY = ((boardRow) * CELLSIZE) +TMARGIN

        xs = CELLSIZE/5    

        # draw the appropriate piece
        pygame.draw.circle (board, PCOLORS[p], (centerX, centerY), CELLSIZE/3, 0)
    
    def clickBoard(self):
        # determine where the user clicked and if the space is not already
        # occupied, draw the appropriate piece there (Player 1 or 2 color)
        # ---------------------------------------------------------------
        (mouseX, mouseY) = pygame.mouse.get_pos()
        if mouseX >= LMARGIN and mouseX <= LMARGIN+BOARDSIZE:
            if mouseY >= TMARGIN and mouseY <= TMARGIN+BOARDSIZE:
               (row, col) = self.boardPos (mouseX, mouseY)
               self.model.TakeTurn(row,col)

    def ReDraw(self,s):
        #re-fill the background
        s.fill (BACKCOLOR)
        #re-draw game board onto surface s
        self.DrawSquares(s)
        #re-draw pieces
        for cell in self.model.M:
            if cell:
                self.drawMove(s,self.model.M.row,self.model.M.col,cell-1)                    
        self.DrawCaptures(s,self.model.Captures)
        #draw dot on most recently placed piece
        pygame.draw.circle(s,WHITE,(LMARGIN+self.model.lastmove[1]*CELLSIZE, \
                                    TMARGIN+self.model.lastmove[0]*CELLSIZE),2,0)

class PenteAI:
    def __init__(self,m):
        self.model = m
        self.votes = Matrix(m.size,0)
        self.scores = [i for i in range(self.model.NumPlayers)]
        self.size = m.size
    def CaptureSetups(self,m,runs,p):
        #count how many capture setups we have (pairs with opponent on one end)
        result=0
        for run in runs[2]:
            if len(m.GetEnds(2,run))==2 and len(m.GetOpenEnds(2,run))==1:
                result += 1
        return result

    def OpenRuns(self,m,runs,p,n):
        #Counts the number of open-ended runs of length n, for player p
        result = 0
        for run in runs[n]:
            if len(m.GetOpenEnds(n,run))==2:
                result += 1
        return result
    def ClosedRuns(self,m,runs,p,n):
        #Counts the number of closed-ended runs of length n, for player p
        result = 0
        for run in runs[n]:
            endlist = m.GetEnds(n,run)
            oendlist = m.GetOpenEnds(n,run)
            if len(oendlist)<2 and len(endlist)>0:
                result += 1
        return result

    def MakeMove(self):
        m=self.model
        # strategies:
        A = -500 # move onto a space already taken!
        B = 8    # move to the end of an opponent's open pair (start a trap)
        C = 10   # move to cap an open three (block a win)
        D = 2    # move to cap a one-ended three (keep it from growing)
        E = 20   # move to cap any run of four (try to block a win)
        F = -1   # move to all edge locations (not good for building runs)
        G = 1    # G+n to move to add an intersection (building complexity and multiple runs), n=number of neighbors
        H = 1    # H+n to move to block an opponent intersection (defense), n=number of neighbors
        I = 20   # move to make a threesome (closed on one side) - prevents a trap
        J = 8    # move to make an open three out of a pair - can lead to a winner
        K = 4    # move to make four in a row
        L = 30   # move to make an open four in a row
        M = 35   # move to make five in a row (win the game)
        N = 25   # move to prevent an open four opponent pieces
        O = 25   # move to prevent a run of five opponent pieces
        P = 10   # move to prevent an open-three opportunity
        Q = 20   # move to capture an opponent
        
        # These rules have not been implemented yet:
        #P = 3    # move to one space away from an existing piece of ours (sets up an intersection fill later)
        #Q = -2   # move to make a closed-end pair (sets up a trap opportunity for opponent)
        #R = -1   # move to make an open pair (could lead to trap)
                             
        # Clear votes, and don't move onto a space already taken
        for cell in self.votes:
            self.votes.matrix[self.votes.row][self.votes.col]=0
            if m.M.matrix[self.votes.row][self.votes.col]<>0:
                self.votes.matrix[self.votes.row][self.votes.col] += A

        # move to the end of an opponent's open pair (try to trap)
        for run in m.Runs[HUMAN][2]:
            endlist = m.GetEnds(2,run)
            if len(endlist)==2: #ignore runs that are on the edge of the board
                oendlist = m.GetOpenEnds(2,run)
                for pair in oendlist:
                  if len(oendlist)==2:  #open pair - set up a trap
                    self.votes.matrix[pair[0]][pair[1]] += B
                    if DEBUG: print "found end of opponent's open pair"
                  if len(oendlist)==1:  #closed pair - spring the trap!
                    if DEBUG: print "found chance to capture opponent"
                    self.votes.matrix[pair[0]][pair[1]] += Q

        # move to cap an open three (block a win)
        for run in m.Runs[HUMAN][3]:
            endlist = m.GetOpenEnds(3,run)
            if len(endlist)==2: #ignore pairs at edge of board
              for pair in endlist:
                  self.votes.matrix[pair[0]][pair[1]] += C
                  if DEBUG: print "found opponent's open three"

        # move to cap a one-ended three (keep it from growing)
        for run in m.Runs[HUMAN][3]:
            endlist = m.GetOpenEnds(3,run)
            if len(endlist)==1: #focus on runs with only one open end
                self.votes.matrix[endlist[0][0]][endlist[0][1]] += D
                if DEBUG: print "found one-ended open three"

        # move to cap any run of four (try to block a win)
        for run in m.Runs[HUMAN][4]:
            endlist = m.GetEnds(4,run)
            for pair in endlist:
                 self.votes.matrix[pair[0]][pair[1]] += E
                 if DEBUG: print "found a run of four"

        # move to all edge locations (not good for building runs)
        for c in range(m.size):
            self.votes.matrix[c][0] += -1
            self.votes.matrix[c][m.size-1] += F
        for r in range(m.size):
            self.votes.matrix[0][r] += -1
            self.votes.matrix[m.size-1][r] += F

        # move to add an intersection (building complexity and multiple runs)
        for r in range(m.size-1):
            for c in range(m.size-1):
                if m.M.matrix[r][c]==0:
                    n=0  
                    #count how many of our pieces are in neighboring cells
                    for ri in range(r-1,r+2):
                        for ci in range(c-1,c+2):
                            if m.M.matrix[ri][ci]==COMPUTER+1:
                                n += 1
                    self.votes.matrix[r][c] += (G+n)
                    #if DEBUG: print "Added %d for my intersections" % (G+n)

        # move to add an intersection (defense against opponent building complexity)
        for r in range(m.size-1):
            for c in range(m.size-1):
                if m.M.matrix[r][c]==0:
                    n=0  
                    #count how many of our pieces are in neighboring cells
                    for ri in range(r-1,r+2):
                        for ci in range(c-1,c+2):
                            if m.M.matrix[ri][ci]==HUMAN+1:
                                n += 1
                    self.votes.matrix[r][c] += (H+n)
                    #if DEBUG: print "Added %d for opponent intersections" % (G+n)
                    
        # move to make various runs in a row (closed and open)
        threes = len(m.Runs[COMPUTER][3])
        openthrees = self.OpenRuns(m,m.Runs[COMPUTER],COMPUTER,3)
        fours = len(m.Runs[COMPUTER][4])  #get current number of runs of four
        openfours = self.OpenRuns(m,m.Runs[COMPUTER],COMPUTER,4)
        fives = len(m.Runs[COMPUTER][5])  #get current number of runs of five
        for c in range(m.size):
            for r in range(m.size):
                if m.M.matrix[r][c]==0:
                    m.M.matrix[r][c]= COMPUTER+1
                    m.CalcStats()
                    if len(m.Runs[COMPUTER][3])>threes:
                        self.votes.matrix[r][c] += I
                        if DEBUG: print "found chance to make a threesome"
                        if self.OpenRuns(m,m.Runs[COMPUTER],COMPUTER,3) > openthrees:
                            self.votes.matrix[r][c] += J
                            if DEBUG: print "Found chance to make an OPEN three"
                    if len(m.Runs[COMPUTER][4])>fours:
                        self.votes.matrix[r][c] += K
                        if DEBUG: print "found chance to make a foursome"
                        if self.OpenRuns(m,m.Runs[COMPUTER],COMPUTER,4) > openfours:
                            self.votes.matrix[r][c] += L
                            if DEBUG: print "found chance to make an OPEN foursome"
                    if len(m.Runs[COMPUTER][5])>fives:
                        self.votes.matrix[r][c] += M
                        if DEBUG: print "found a chance to make a five-some"
                    m.M.matrix[r][c]=0 #undo our move

        # move to fill in a gap in various runs of opponent pieces
        m.CalcStats()
        openthrees = self.OpenRuns(m,m.Runs[HUMAN],HUMAN,3)
        fours = len(m.Runs[COMPUTER][4])  #get current number of runs of four
        openfours = self.OpenRuns(m,m.Runs[HUMAN],HUMAN,4)
        for c in range(m.size):
            for r in range(m.size):
                if m.M.matrix[r][c]==0:
                    m.M.matrix[r][c]= HUMAN+1
                    m.CalcStats()
                    if len(m.Runs[HUMAN][5])>0:
                        self.votes.matrix[r][c] += O
                        if DEBUG: print "Found chance to block a five-run"
                    if len(m.Runs[HUMAN][4])>fours:
                        if self.OpenRuns(m,m.Runs[HUMAN],HUMAN,4) > openfours:
                            self.votes.matrix[r][c] += N
                            if DEBUG: print "found a chance to block an oppponents open-four opportunity"
                    if self.OpenRuns(m,m.Runs[HUMAN],HUMAN,3) > openthrees:
                        self.votes.matrix[r][c] += P
                        if DEBUG: print "Found chance to block open three opportunity"
                    m.M.matrix[r][c]=0 #undo our move


    # -------------------------------------------------
        #evaluate votes and decide move
        options = m.PickCells(self.votes,max(self.votes))
        rm,cm = options[randint(0,len(options)-1)]
        m.TakeTurn(rm,cm)
        m.CalcStats()
        
        
# -------------------------------------------------------
# Beginning of Main Loop
# Define Constants

# create a model instance
model = PenteModel(SIZE)
# create a view instance
view = PenteView(model,BOARDSIZE)
# create an AI instance
ai = PenteAI(model)

# --------------------------------------------------------------------
# initialize pygame and our window
pygame.init()
P1click = pygame.mixer.Sound("QABITEM.WAV")
P2click = pygame.mixer.Sound("Windows XP Balloon.wav")
laugh = pygame.mixer.Sound("giddylaugh.wav")
ohhh = pygame.mixer.Sound("ohhh.wav")

#debug
##model.M.matrix[0][0]=2
##model.M.matrix[3][4]=2
##model.M.matrix[4][3]=2
##model.wins[0] = 12
##model.wins[1] = 17
##model.Captures=[4,4]
#view.ReDraw(view.board)

# main event loop
running = 1
done = 0

while not done:
  while (running == 1):
    for event in pygame.event.get():
        if event.type is QUIT:
            running = 0  #stop event loop
            done = 1     #stop program
        elif event.type is MOUSEBUTTONDOWN:
            # the user clicked; place a piece
            view.clickBoard()
            # refresh the board
            view.ReDraw(view.board)
            # play click sound
            P1click.play()
            # log statistics
            model.CalcStats()
        # check for a winner
        model.gameWon()

        # update the display
        view.showBoard (view.ttt, view.board, model.Turn, model.Winner)

        # Check for a winner
        if model.Winner<>None:
            view.ReDraw(view.board)
            view.showBoard(view.ttt, view.board, model.Turn, model.Winner)
            running = 0; #stop event loop

        # Let the computer take a turn
        if model.Turn == COMPUTER and model.Winner==None:
            ai.MakeMove()
            # re-draw the board
            view.ReDraw(view.board)
            # play click sound
            P2click.play()

  for event in pygame.event.get():
        if event.type is QUIT:
            done = 1     #stop program
        elif event.type is MOUSEBUTTONDOWN:
            # the user clicked; start a new game
            model.wins[(model.Turn+1)%2] += 1  #increment the win counter
            model.Reset()  #reset game state
            view.ReDraw(view.board)
            view.showBoard(view.ttt, view.board, model.Turn, model.Winner)
            running = 1    #start running game again
            
            