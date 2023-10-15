KeyAction = None
Menu = None
MenuMgr = None

import msvcrt
from typing import Callable
import readchar
from utils import Utils

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
    ):
        self.header = header
        self.keyActions = keyActions
        self.intent = intent
        self.defaultAction = defaultAction


class MenuMgr:
    curMenu = None
    keyRunning = False
    onTickStartActions = []

    def executeKeyAction(keyName: str):
        if MenuMgr.curMenu == None or MenuMgr.keyRunning:
            return

        def runAction(keyAction: KeyAction):
            if keyAction.action:
                MenuMgr.keyRunning = True
                keyAction.action()
                MenuMgr.keyRunning = False

        executed = False
        for keyAction in MenuMgr.curMenu.keyActions:
            if keyName == keyAction.key:
                runAction(keyAction)
                executed = True
                break

        if not executed:
            if MenuMgr.curMenu.defaultAction != None:
                MenuMgr.curMenu.defaultAction()
                executed = True

    def displayMenu(menu: Menu):
        if menu == None:
            return

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
        Utils.printInline(intendStr + "输入: ")

    def switchMenu(menu: Menu):
        MenuMgr.curMenu = menu

    def onTickStart(action: Callable):
        MenuMgr.onTickStartActions.append(action)

    def removeOnTickStart(action: Callable):
        MenuMgr.onTickStartActions.remove(action)

    def startMenu():
        while True:
            for action in MenuMgr.onTickStartActions:
                action()

            MenuMgr.displayMenu(MenuMgr.curMenu)

            inputKey = readchar.readkey()
            Utils.printInline(inputKey + "\n")
            MenuMgr.executeKeyAction(inputKey)

            # 清除在执行命令期间输入的命令
            while msvcrt.kbhit():
                msvcrt.getch()
