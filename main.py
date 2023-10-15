from mainMenu import MainMenu
from program import Program
from menuMgr import MenuMgr

MenuMgr.onTickStart(Program.initializeTick)

MenuMgr.switchMenu(MainMenu.getMenu())
#MenuMgr.startMenu()
Program.initializeTick()
