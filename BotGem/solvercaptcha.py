import os, cv2, time
import numpy as np
from twocaptcha import TwoCaptcha

class SolverCaptcha():
    def __init__(self, emulator):
        self.emulator = emulator
        
    def ScreenCapture(self, name):
        os.system(f'adb -s {self.emulator} exec-out screencap -p > ./images/{name}')

    def Click(self, x, y):
        os.system(f'adb	-s {self.emulator} shell input tap {x} {y}')
        
    def ClickTemplate(self, screenshot, template):
        img = cv2.imread(os.path.join('images', screenshot), cv2.IMREAD_GRAYSCALE)
        img_gray = cv2.convertScaleAbs(img)

        template = cv2.imread(os.path.join('images', template), cv2.IMREAD_GRAYSCALE)
        template = cv2.convertScaleAbs(template)

        # Find template in the image
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

    def Find(self, screenshot, template):
        img_rgb = cv2.imread(os.path.join('images', screenshot))
        template = cv2.imread(os.path.join('images', template))

        result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        locations = []
        threshold = 0.85
        loc = np.where(result >= threshold)
        if len(loc[0]) > 0:
            for pt in zip(*loc[::-1]):
                locations.append(pt)
        return locations
    
    # Giải captcha
    def SolverCaptcha(self, ROK):
        for i in range(2):
            self.ScreenCapture('captcha.bmp')
            lenCaptcha1 = self.Find('captcha.bmp', 'CaptchaAppearIcon1.bmp')
            lenCaptcha2 = self.Find('captcha.bmp', 'CaptchaAppearIcon2.bmp')
            if len(lenCaptcha1) > 0 or len(lenCaptcha2) > 0:
                print("Phát hiện captcha. Giải captcha")
                if len(lenCaptcha1) > 0:
                    self.Click(lenCaptcha1[0][0], lenCaptcha1[0][1])
                if len(lenCaptcha2) > 0:
                    self.Click(lenCaptcha2[0][0], lenCaptcha2[0][1])
                time.sleep(3)
                for count in range(10):
                    self.ScreenCapture('captcha.bmp')
                    lenVerifyButton = self.Find('captcha.bmp', 'VerifyButton.bmp')
                    if len(lenVerifyButton) > 0:
                        self.ClickTemplate('captcha.bmp', 'VerifyButton.bmp')
                        break
                    elif len(lenVerifyButton) == 0:
                        time.sleep(1)

                time.sleep(5)
                for count in range(5):
                    self.ScreenCapture('captcha.bmp')
                    lenCaptchaShow = self.Find('captcha.bmp', 'CaptchaShow.bmp')
                    if len(lenCaptchaShow) > 0:
                        time.sleep(5)
                        self.CropCaptcha()
                        self.SendCaptcha(ROK)
                        self.ScreenCapture('captcha.bmp')
                        lenCheckCaptcha = self.Find('captcha.bmp', 'CheckCaptcha.bmp')
                        if len(lenCheckCaptcha) == 0:
                            break
                        else:
                            print("Giải captcha sai. Giải lại")
                    else:
                        time.sleep(1)
                break
            elif i == 0:
                print("Không phát hiện captcha. Kiểm tra lại")
            else:
                print("Không phát hiện captcha")

    def CropCaptcha(self):
        imagecaptcha = cv2.imread('./images/captcha.bmp')
        cropcaptcha = imagecaptcha[100:620, 435:840]
        cv2.imwrite('./images/cropcaptcha.jpg', cropcaptcha)

    def SendCaptcha(self, ROK):
        captcha_path = './images/cropcaptcha.jpg'
        api_key = '310ec631bdd1f94a868f1805d7bef36c'
        solver = TwoCaptcha(api_key, defaultTimeout=120, pollingInterval=5)

        try:
            print("Gửi captcha")
            result = solver.coordinates(captcha_path, lang='en')
        except Exception as e:
            print("Lỗi Captcha", e)
            os.system(f"adb -s {self.emulator} shell am force-stop {ROK}")
            os.system(f'adb -s {self.emulator} shell am start -n {ROK}/com.harry.engine.MainActivity')
            time.sleep(60)
            self.SolverCaptcha(ROK)
        else:
            print("Giải captcha thành công")
            result_captcha = result
            self.Click_captcha(result_captcha)

    # Click captcha
    def Click_captcha(self, result):
        result_captcha = result
        captcha = result_captcha['code']
        coordinate = captcha.replace('coordinates:', '').split(';')
        print(coordinate)

        for pair in coordinate:
            x, y = pair.split(',')
            x = x.split('=')[1]
            y = y.split('=')[1]
            os.system(f'adb	-s {self.emulator} shell input tap {int(x) + 435} {int(y) + 100}')
            time.sleep(1)
        self.Click(760, 587)
        time.sleep(5)