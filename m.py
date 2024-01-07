import ctypes
import keyboard


def show_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(whnd, 1)


def hide_window():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    ctypes.windll.user32.ShowWindow(whnd, 0)


def on_hit(e):
    if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift") and keyboard.is_pressed("g"):
        show_window()


keyboard.hook(on_hit)
keyboard.wait('esc')
