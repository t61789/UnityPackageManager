KeyAction = None
Menu = None
MenuMgr = None

import msvcrt
from typing import Callable
import readchar
from utils import *

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
        global keyRunning
        if curMenu == None or keyRunning:
            return

        def runAction(keyAction: KeyAction):
            global keyRunning
            if keyAction.action:
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
        printInline(intendStr + "输入: ")

    def switchMenu(menu: Menu):
        global curMenu
        curMenu = menu

    def onTickStart(action: Callable):
        MenuMgr.onTickStartActions.append(action)

    def removeOnTickStart(action: Callable):
        MenuMgr.onTickStartActions.remove(action)

    def startMenu():
        while True:
            for action in MenuMgr.onTickStartActions:
                action()

            MenuMgr.displayMenu(curMenu)

            inputKey = readchar.readkey()
            printInline(inputKey + "\n")
            MenuMgr.executeKeyAction(inputKey)

            # 清除在执行命令期间输入的命令
            while msvcrt.kbhit():
                msvcrt.getch()
