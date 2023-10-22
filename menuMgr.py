import msvcrt
from typing import Callable
import readchar
import utils


class KeyAction:
    def __init__(self, key: str, describe: str, action: Callable):
        self.key = key
        self.describe = describe
        self.action = action


class Menu:
    def __init__(
        self,
        header: str or Callable[[str]],
        keyActions: [KeyAction],
        intent: int = 0,
        defaultAction: Callable = None,
        newLine: bool = False,
    ):
        self.header = header
        self.keyActions = keyActions
        self.intent = intent
        self.defaultAction = defaultAction
        self.newLine = newLine


menus = {}
curMenu = Menu(None, None)
keyRunning = False
onTickStartActions = []

PACKAGE_ERROR_MENU = "pacakgeErrorMenu"
CONFIG_ERROR_MENU = "configErrorMenu"
MAIN_MENU = "mainMenu"
MOVE_OUT_PACKAGE_MENU = "moveOutPackageMenu"
MODIFY_PACKAGE_JSON_MENU = "modifyPackageJsonMenu"


def executeKeyAction(keyName: str):
    if curMenu == None or keyRunning:
        return

    def runAction(keyAction: KeyAction):
        if keyAction.action:
            global keyRunning
            keyRunning = True
            keyAction.action()
            keyRunning = False

    executed = False
    for keyAction in curMenu.keyActions:
        if keyName == keyAction.key:
            runAction(keyAction)
            executed = True
            break

    if not executed:
        if curMenu.defaultAction != None:
            curMenu.defaultAction()
            executed = True


def displayMenu(menu: Menu):
    if menu == None:
        return

    if menu.newLine:
        print()

    intendStr = ""
    for i in range(menu.intent):
        intendStr += "  "

    if menu.header != None:
        if isinstance(menu.header, str):
            print(intendStr + menu.header)
        elif callable(menu.header):
            menu.header()

    for keyAction in menu.keyActions:
        print(intendStr, keyAction.key, ": ", keyAction.describe)
    utils.printInline(intendStr + "输入: ")


def switchMenu(menuName: str):
    global curMenu
    curMenu = menus[menuName]


def registerMenu(menuName: str, menu: Menu):
    menus[menuName] = menu


def onTickStart(action: Callable):
    onTickStartActions.append(action)


def removeOnTickStart(action: Callable):
    onTickStartActions.remove(action)


def startMenu():
    while True:
        for action in onTickStartActions:
            action()

        displayMenu(curMenu)

        inputKey = readchar.readkey()
        utils.printInline(inputKey + "\n")
        executeKeyAction(inputKey)

        # 清除在执行命令期间输入的命令
        while msvcrt.kbhit():
            msvcrt.getch()
