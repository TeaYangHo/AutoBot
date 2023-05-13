import os, cv2, time
import subprocess
import numpy as np


class ADB():
    def __init__(self, emulator):
        self.emulator = emulator

    def screen_capture(self, name):
        os.system(f'adb -s {self.emulator} exec-out screencap -p > ./images/{name}')

    def click(self, x, y):
        os.system(f'adb	-s {self.emulator} shell input tap {x} {y}')

    # Find and click template in image
    def click_template(self, screenshot, template):
        self.screen_capture('screenshot.bmp')
        # read images
        img = cv2.imread(os.path.join('images', screenshot))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_gray = cv2.convertScaleAbs(img_gray)

        template = cv2.imread(os.path.join('images', template), 0)
        template = cv2.convertScaleAbs(template)

        # find template in the image
        result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8

        locations = np.where(result >= threshold)
        if len(locations[0]) > 0:
            x, y = int(np.mean(locations[1])), int(np.mean(locations[0]))
            # click on the template
            w, h = template.shape[::-1]
            x_image = x + w / 2
            y_image = y + h / 2
            os.system(f'adb	-s {self.emulator} shell input tap {x_image} {y_image}')
        time.sleep(1)

    # Find template in image
    def find(self, screenshot, template):
        self.screen_capture('screenshot.bmp')
        img_rgb = cv2.imread(os.path.join('images', screenshot))
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
        template = cv2.imread(os.path.join('images', template), 0)

        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        locations = np.where(res >= threshold)
        return locations

    def search_coordinate(self, sever, x_coordinate, y_coordinate):
        delay = time.sleep(1)

        while True:
            if len(self.find('screenshot.bmp', 'confirmbutton.png')[0]) == 0:
                break
            else:
                self.click_template('screenshot.bmp', 'confirmbutton.png')
                time.sleep(10)

        if len(self.find('screenshot.bmp', 'OutCity.png')[0]) > 0:
            self.click(60, 660)
            time.sleep(2)


        # Click search bar
        self.click(435, 20)
        delay
        while True:
            if len(self.find('screenshot.bmp', 'searchbutton.png')[0]) > 0:
                break
            else:
                self.click(435, 20)
                delay

        if len(sever) == 6:
            self.input_coordinate(x_coordinate, y_coordinate)
        elif len(sever) == 4:
            self.click(447, 130)
            for i in range(6):
                os.system(f'adb -s {self.emulator} shell input keyevent KEYCODE_DEL')

            os.system(f'adb -s {self.emulator} shell input text "{sever}"')
            os.system(f'adb -s {self.emulator} shell input keyevent ENTER')
            delay
            self.input_coordinate(x_coordinate, y_coordinate)
        delay

    def input_coordinate(self, x_coordinate, y_coordinate):
        delay = time.sleep(1)
        # Click X-Coordinate
        self.click(634, 130)
        os.system(f'adb -s {self.emulator} shell input text "{x_coordinate}"')
        os.system(f'adb -s {self.emulator} shell input keyevent ENTER')
        delay

        # Click Y-Coordinate
        self.click(787, 130)
        os.system(f'adb -s {self.emulator} shell input text "{y_coordinate}"')
        os.system(f'adb -s {self.emulator} shell input keyevent ENTER')
        delay

        # Search Coordinates
        self.click(885, 130)
        time.sleep(7)

    def click_home(self):
        if (len(self.find('screenshot.bmp', 'MarkersButton.png')[0]) > 0) and (
                len(self.find('screenshot.bmp', 'Navbar.png')[0]) == 0):
            self.click(640, 360)
        time.sleep(3)
        self.click(640, 360)
        time.sleep(1)
        self.click_template('screenshot.bmp', 'title.png')
        time.sleep(1)
        while True:
            if len(self.find('screenshot.bmp', 'checktitle.png')) > 0:
                break
            else:
                self.click_template('screenshot.bmp', 'title.png')
                time.sleep(1)


    def title_duke(self):
        # Duke X Y
        self.click(520, 390)
        time.sleep(1)
        # CONFIRM X Y
        self.click(645, 635)

    def title_architect(self):
        # Architect X Y
        self.click(750, 390)
        time.sleep(1)
        # CONFIRM X Y
        self.click(645, 635)

    def title_scientist(self):
        # Scientist X Y
        self.click(980, 390)
        time.sleep(1)
        # CONFIRM X Y
        self.click(645, 635)

    def reset_ROK(self):
        memu_folder = r"D:\Program Files\Microvirt\MEmu"
        subprocess.run(["cmd.exe", "/c", f"cd {memu_folder} && MEmuConsole ShutdownVm MEmu"])
        subprocess.run(["cmd.exe", "/c", f"cd {memu_folder} && MEmuConsole MEmu"])
        time.sleep(30)
        os.system(f'adb -s {self.emulator} shell am start -n com.rok.gp.vn/com.harry.engine.MainActivity')
#
# if __name__ == '__main__':
#     ADB_DEVICE = '127.0.0.1:21503'
#     adb = ADB(ADB_DEVICE)
#     adb.reset_ROK()