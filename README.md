# python-pente
Python based Pente game, with AI player

#Pente Game, using Object-Oriented programming techniques
#Randy Gamage
#9-AUG-2005

#Design Notes:
There are four main classes, to separate the tasks roughly along the Model, View, Control type
of design pattern.  The classes are as follows:
* Matrix - A generic matrix object to store and manipulate a two-dimensional array
* PenteModel - The mathematical model that performs analysis/statistics of the pente game
* PenteView - The GUI for the game.  Implemented here using PyGame, but could use any GUI framework
* PenteGame - The game state variables, that keeps track of players and who is winning, etc.
* PenteAI - The Artificial Intelligence class that allows the computer to calculate moves and compete against another player
These constants are all related to the View, but for now we'll make them globals,
just because it's easier and makes for cleaner looking code. Eventually these should
be global only within the View module, but for now all classes are in the same file.

#Deployment notes:
Successfully used py2exe to build this script into a windows .exe file.
It seems to work, even with psyco enabled.
Next task, use Inno Setup and IStool to create a windows installer for it.
* www.istool.org
* www.innosetup.com

#Version Tracking
* Current Major Version = 0
* Major Version 0:
* First major version, initial release through test phases
* Current Minor Version = 1
* Minor Version 1:
* First minor version, still fixing bugs and modifying appearance. No windows gui 'widgets',
* just graphical display (game board and status line).
* Current Build:
* The Build number is kept in the file pente.cfg.  The build script, build.py, increments
* this value at every build, and stores an archive of the source code in the archive folder.
* The file name of the archive is "pente_<full version>.py  The full version
* number is Major+"."+Minor+"."+Build