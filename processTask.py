import queue
from typing import Callable
from utils import Utils
import threading
import time


class ProcessTask:
    def __init__(self, action: Callable[[float], None], maxDrawedNum: int = 20):
        self.maxDrawedNum = maxDrawedNum
        self.action = action
        self.progressionVal = 0
        self.progressionValLock = threading.Lock()
        self.processDoneLock = threading.Lock()
        self.runningMark = ["\\", "-", "/"]
        self.runningMarkIndex = 0
        self.processDone = False
        self.exceptionQueue = queue.Queue()

    def setProgressionVal(self, process):
        self.progressionValLock.acquire()
        self.progressionVal = process
        if process >= 1:
            self.setProcessDone(True)
        self.progressionValLock.release()

    def getProgressionVal(self):
        self.progressionValLock.acquire()
        progressionVal = self.progressionVal
        self.progressionValLock.release()
        return progressionVal

    def setProcessDone(self, processDone):
        self.processDoneLock.acquire()
        self.processDone = processDone
        self.processDoneLock.release()

    def hasProcessDone(self):
        self.progressionValLock.acquire()
        processDone = self.processDone
        self.progressionValLock.release()
        return processDone

    def getRunningMark(self):
        mark = self.runningMark[self.runningMarkIndex]
        self.runningMarkIndex = (self.runningMarkIndex + 1) % len(self.runningMark)
        return mark

    def drawRunningMark(self, drawedNum, runningMark="-"):
        moveLength = self.maxDrawedNum - drawedNum + 2
        Utils.printInline("\x1b[" + str(moveLength) + "C")
        Utils.printInline(runningMark)
        Utils.printInline("\x1b[" + str(moveLength + 1) + "D")

    def drawProgressBarBoarder(self):
        Utils.printInline("[")
        Utils.printInline("\x1b[" + str(self.maxDrawedNum) + "C")
        Utils.printInline("]")
        Utils.printInline("\x1b[" + str(self.maxDrawedNum + 1) + "D")

    def clearRunningMark(self, drawedNum):
        self.drawRunningMark(drawedNum, " ")

    def runAction(self, q, action, setProcessDone, setProgressionVal):
        try:
            action(setProgressionVal)
        except Exception as e:
            setProcessDone(True)
            q.put(e)

    def run(self):
        taskThread = threading.Thread(
            target=self.runAction,
            args=(
                self.exceptionQueue,
                self.action,
                self.setProcessDone,
                self.setProgressionVal
            )
        )
        taskThread.start()
        drawedNum = 0
        self.drawProgressBarBoarder()

        while True:
            time.sleep(0.1)
            process = self.getProgressionVal()

            self.drawRunningMark(drawedNum, self.getRunningMark())

            targetDrawNum = int(process * self.maxDrawedNum)
            while drawedNum < targetDrawNum:
                Utils.printInline("#")
                drawedNum += 1

            if self.hasProcessDone():
                break

        self.clearRunningMark(self.maxDrawedNum)
        Utils.printInline("\x1b[" + str(self.maxDrawedNum - drawedNum + 1) + "C")
        taskThread.join()

        if not self.exceptionQueue.empty():
            raise self.exceptionQueue.get()


def run(action: Callable[[float], None], maxDrawedNum: int = 20):
    ProcessTask(action).run()
