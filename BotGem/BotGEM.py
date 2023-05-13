from adbGEM import ADB
from solvercaptcha import SolverCaptcha
import time, datetime


class BOTGEM(ADB, SolverCaptcha):
    def __init__(self, emulator):
        super().__init__(emulator)

    def run_emulator(self, MEmu, ROK):
        adb = ADB(self.emulator)
        captcha = SolverCaptcha(self.emulator)
        #adb.start(MEmu, ROK)
        #captcha.SolverCaptcha(ROK)
        #adb.checkOutCity()
        adb.zoomOut(MEmu)
        adb.swipe(MEmu, ROK)
        #adb.find_gem()
        # time.sleep(5)
        # captcha.SolverCaptcha(ROK)



QT = 'com.lilithgame.roc.gp'
VN = 'com.rok.gp.vn'
BOTGEM('127.0.0.1:21513').run_emulator('MEmu_1', VN)