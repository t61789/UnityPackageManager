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
COPY_TO_RF_PROJECT_CONFIRM_MENU = "copyToRfProjectConfirmMenu"


def executeKeyAction(keyAction):
    if keyAction.action:
        global keyRunning
        keyRunning = True
        keyAction.action()
        keyRunning = False


def findAvailableAction(keyName: str) -> KeyAction:
    if curMenu == None or keyRunning:
        return None

    for keyAction in curMenu.keyActions:
        if keyName == keyAction.key:
            return keyAction

    if curMenu.defaultAction:
        return curMenu.defaultAction

    return None


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

        while True:
            inputKey = readchar.readkey()
            keyAction = findAvailableAction(inputKey)
            if not keyAction:
                continue

            utils.printInline(inputKey + "\n")
            executeKeyAction(keyAction)

            # 清除在执行命令期间输入的命令
            while msvcrt.kbhit():
                msvcrt.getch()
            break


def confirmMenu(tile: str) -> bool:
    utils.printInline(tile + " [E/Q]")
    while True:
        inputKey = readchar.readkey()
        if inputKey == "e":
            print("e")
            return True
        elif inputKey == "q":
            print("q")
            return False
