import os, cv2, time, subprocess
import numpy as np
import pyautogui

from swipe import Swipe

class ADB(Swipe):
    def __init__(self, emulator):
        super().__init__(emulator)

    def screen_capture(self, name):
        os.system(f'adb -s {self.emulator} exec-out screencap -p > ./images/{name}')

    def click(self, x, y):
        os.system(f'adb	-s {self.emulator} shell input tap {x} {y}')

    def back(self):
        os.system(f'adb	-s {self.emulator} shell input keyevent 4')

    def click_template(self, template):
        self.screen_capture("ScreenShot.bmp")
        img = cv2.imread(os.path.join('images', "ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
        img_gray = cv2.convertScaleAbs(img)

        template = cv2.imread(os.path.join('images', template), cv2.IMREAD_GRAYSCALE)
        template = cv2.convertScaleAbs(template)

        result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8

        locations = np.where(result >= threshold)
        if len(locations[0]) > 0:
            x, y = int(np.mean(locations[1])), int(np.mean(locations[0]))
            w, h = template.shape[::-1]
            x_image = x + w / 2
            y_image = y + h / 2
            os.system(f'adb	-s {self.emulator} shell input tap {x_image} {y_image}')

    def find(self, template):
        self.screen_capture("ScreenShot.bmp")
        img_rgb = cv2.imread(os.path.join('images',"ScreenShot.bmp"))
        template = cv2.imread(os.path.join('images', template))

        result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        locations = []
        threshold = 0.85
        loc = np.where(result >= threshold)
        if len(loc[0]) > 0:
            for pt in zip(*loc[::-1]):
                locations.append(pt)
        return locations



    def start(self, MEmu, ROK):
        memu_folder = r"D:\Program Files\Microvirt\MEmu"
        print("Bắt đầu thu thập tài nguyên")
        print("Khời động MEmu")
        subprocess.run(["cmd.exe", "/c", f"cd {memu_folder} && MEmuConsole {MEmu}"])
        time.sleep(45)
        print("Khởi động Rise of Kingdoms")
        os.system(f'adb -s {self.emulator} shell am start -n {ROK}/com.harry.engine.MainActivity')
        time.sleep(60)
        self.checkConfirm(MEmu, ROK)

    def end(self, MEmu):
        memu_folder = r"D:\Program Files\Microvirt\MEmu"
        print("Kết thúc thu thập tài nguyên")
        subprocess.run(["cmd.exe", "/c", f"cd {memu_folder} && MEmuConsole ShutdownVm {MEmu}"])
        time.sleep(5)

    def checkConfirm(self, MEmu, ROK):
        checkCF = self.find('confirmbutton.bmp')
        if len(checkCF) == 0:
            print("Hoạt động bình thường")
        else:
            print("Mất kết nối. Khởi động lại")
            self.end(MEmu)
            self.start(MEmu, ROK)

    def checkOutCity(self):
        for i in range(3):
            checkCity = self.find('OutCity.bmp')
            if len(checkCity) == 0:
                print("Không quan sát ở trong thành phố")
                break
            elif len(checkCity) > 0:
                print("Đang quan sát ở trong thành phố")
                print("Rời khỏi và thu thập tài nguyên")
                self.click(60, 660)
                time.sleep(2)
            break

    def checkStatus(self, MEmu, ROK):
        self.checkConfirm(MEmu, ROK)
        ToInsideCity = self.find("ToInsideCity.bmp")
        if len(ToInsideCity) > 0:
            print("Trạng thái bình thường")
        else:
            print("Phát hiện bất thường. Kiểm tra lại trạng thái!")
            for i in range(5):
                self.back()
                time.sleep(1)
                Calcel = self.find("CalcelButton.bmp")
                if len(Calcel) > 0:
                    self.click(Calcel[0][0], Calcel[0][1])
                    time.sleep(1)
                    self.checkOutCity()
                    break
                else:
                    self.back()

    def gather(self, MEmu, ROK):
        self.click(640, 360)
        time.sleep(1)
        self.screen_capture('ScreenShot.bmp')
        GatherButton = self.find('GatherButton.bmp')
        if len(GatherButton) > 0:
            self.click(GatherButton[0][0], GatherButton[0][1])
        else:
            self.checkStatus(MEmu, ROK)
            #self.zoomOut(MEmu)
        time.sleep(2)
        self.click_template('NewTroopButton.bmp')
        time.sleep(3)
        self.checkSlot()

    def checkSlot(self):
        x = 1100
        y = [290, 350, 410, 470, 530]
        slot = ['Slot1.bmp', 'Slot2.bmp', 'Slot3.bmp', 'Slot4.bmp', 'Slot5.bmp']
        for i in range(5):
            self.click(x, y[i])
            time.sleep(1)
            checkSlot = self.find(slot[i])
            if len(checkSlot) > 0:
                print("Đạo quân sẵn sàng")
                self.click(930, 630)
                break

    def find_gem(self, MEmu, ROK):
        self.screen_capture('ScreenShot.bmp')
        img = cv2.imread(os.path.join('images', 'ScreenShot.bmp'))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.convertScaleAbs(img_gray)
        template_file = ['GemDeposit0.bmp', 'GemDeposit1.bmp', 'GemDeposit2.bmp', 'GemDeposit3.bmp', 'GemDeposit4.bmp',
                         'GemDeposit5.bmp', 'GemDeposit6.bmp', 'GemDeposit7.bmp', 'GemDeposit8.bmp', 'GemDeposit9.bmp',
                         'GemDepositZ1.bmp', 'GemDepositZ2.bmp', 'GemDepositZ3.bmp', 'GemDepositZ4.bmp']

        for template in template_file:
            template = cv2.imread(os.path.join('images', template), 0)
            template = cv2.convertScaleAbs(template)
            result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
            threshold = 0.8
            locations = np.where(result >= threshold)
            if len(locations[0]) > 0:
                x, y = int(np.mean(locations[1])), int(np.mean(locations[0]))
                w, h = template.shape[::-1]
                x_image = x + w / 2
                y_image = y + h / 2
                print("Tìm thấy gem: ", x_image, y_image)
                self.click(x_image, y_image)
                time.sleep(3)
                if len(self.checkGEM()) > 0:
                    print("Mỏ tài nguyên đang có quân đến thu thập")
                    print("Tìm kiếm mỏ tiếp theo")
                    self.zoomOut(MEmu)
                else:
                    print("Mỏ tài nguyên không có quân đến thu thập")
                    self.gather(MEmu, ROK)
                    self.zoomOut(MEmu)
                break

    def checkGEM(self):
        self.screen_capture('ScreenShot.bmp')
        image = cv2.imread(os.path.join('images', 'ScreenShot.bmp'))
        ResourceMine = image[200:520, 460:820]
        # cv2.imwrite('./images/ResourceMine.bmp', ResourceMine)

        img = ResourceMine
        img = cv2.convertScaleAbs(img)
        template_file = ['ComingByEnemy1.bmp', 'ComingByEnemy2.bmp', 'ComingByMember1.bmp', 'ComingByMember2.bmp',
                         'ComingBySelf1.bmp', 'ComingBySelf2.bmp', 'GatheringBySelf.bmp', 'GatheringByMember.bmp',
                         'GatheringByEnemy.bmp']
        locations = []
        threshold = 0.8
        for template in template_file:
            template = cv2.imread(os.path.join('images', template))
            template = cv2.convertScaleAbs(template)
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(result >= threshold)
            if len(loc[0]) > 0:
                for pt in zip(*loc[::-1]):
                    locations.append(pt)
        return locations

    def checkFull(self):
        full = self.find('AllArmiesBusy.bmp')
        if len(full) > 0:
            #print("Full")
            status = True
        else:
            #print("Chuaw full")
            status = False

        return status
    def swipe(self, MEmu, ROK):
        swipe = 1
        actions = [self.swipeRight, self.swipeDown, self.swipeLeft, self.swipeUp]
        current_action = 0
        while True:
            if current_action == 2:
                swipe += 1
            for i in range(swipe):
                actions[current_action]()
                self.find_gem(MEmu, ROK)

            full = self.find('AllArmiesBusy.bmp')
            if len(full) > 0:
                break


            current_action = (current_action + 1) % len(actions)
            if current_action == 0:
                swipe += 1

    def zoomOut(self, MEmu):
        memu_folder = r"D:\Program Files\Microvirt\MEmu"
        subprocess.run(["cmd.exe", "/c", f"cd {memu_folder} && MEmuConsole {MEmu}"])
        time.sleep(1)
        pyautogui.press('~')
        time.sleep(5)
        checkToWorld = self.find('ToWorld.bmp')
        checkNavbar = self.find('Navbar.bmp')

        if len(checkToWorld) > 0 or len(checkNavbar) > 0:
            self.click_template('ToInsideCity.bmp')
            time.sleep(3)
            self.checkOutCity()
            time.sleep(1)
            self.zoomOut(MEmu)

if __name__ == '__main__':
    emulator = '127.0.0.1:21513'
    adb = ADB(emulator)
    adb.screen_capture('ScreenShot.bmp')
    VN = 'com.rok.gp.vn'
    adb.swipe('MEmu_1', VN)