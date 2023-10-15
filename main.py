Main = None

from utils import *
from mainMenu import *
from program import *
from menuMgr import *

MenuMgr.onTickStart(Program.initializeTick)

MenuMgr.switchMenu(MainMenu.getMenu())
MenuMgr.startMenu()
