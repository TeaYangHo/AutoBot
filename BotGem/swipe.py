import time, os

class Swipe():
    def __init__(self, emulator):
        self.emulator = emulator

    def swipeRight(self):
        os.system(f'adb -s {self.emulator} shell input touchscreen swipe 640 360 0 360 500')
        time.sleep(2)

    def swipeLeft(self):
        os.system(f'adb -s {self.emulator} shell input touchscreen swipe 640 360 1280 360 500')
        time.sleep(2)

    def swipeDown(self):
        os.system(f'adb -s {self.emulator} shell input touchscreen swipe 640 360 640 0 500')
        time.sleep(2)

    def swipeUp(self):
        os.system(f'adb -s {self.emulator} shell input touchscreen swipe 640 150 640 720 500')
        time.sleep(2)
