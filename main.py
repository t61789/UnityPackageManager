import menuMgr
import program
import moveOutPackage
import mainMenu
import modifyPackageVersion
import os

# TODO 兼容WindowsTerminal路径
os.system("")

menuMgr.onTickStart(program.initializeTick)

menuMgr.switchMenu(menuMgr.MAIN_MENU)
menuMgr.startMenu()
