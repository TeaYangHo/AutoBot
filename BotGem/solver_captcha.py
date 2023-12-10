from adb import *
from twocaptcha import TwoCaptcha
import time


def find_captcha(devices):
	screen_capture(devices, f"captcha.bmp")
	image = cv2.imread(os.path.join("images", f"captcha.bmp"), cv2.IMREAD_GRAYSCALE)
	template_file = ["CaptchaAppearIcon1.bmp", "CaptchaAppearIcon2.bmp", "CaptchaAppearIcon3.bmp", "CaptchaAppearIcon4.bmp", "CaptchaAppearIcon5.bmp"]
	locations = []
	threshold = 0.9
	for template in template_file:
		template = cv2.imread(os.path.join("images", template), cv2.IMREAD_GRAYSCALE)
		template = cv2.convertScaleAbs(template)
		result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			for pt in zip(*loc[::-1]):
				locations.append(pt)
	if len(locations) > 0:
		return locations[0]


def solver_(devices, rok):
	for i in range(5):
		screen_capture(devices, f"captcha.bmp")
		len_captcha_show = find_template(devices, "CaptchaShow.bmp")
		if len_captcha_show:
			time.sleep(5)
			crop_captcha()
			send_captcha(devices, rok)
			screen_capture(devices, f"captcha.bmp")
			len_check_captcha = find_template(devices, "CheckCaptcha.bmp")
			if not len_check_captcha:
				break
			else:
				print("Giải captcha sai. Giải lại")
		else:
			time.sleep(2)


def solver_captcha(devices, rok):
	verify_button_captcha = find_template(devices, "VerifyButton.bmp")
	captcha = find_captcha(devices)
	if verify_button_captcha:
		print("Detect captchas!")
		click(devices, verify_button_captcha[0], verify_button_captcha[1], 5)
		solver_(devices, rok)

	elif captcha:
		print("Detect captchas!")
		click(devices, captcha[0], captcha[1], 1.5)
		for count in range(10):
			len_verify_button = find_template(devices, "VerifyButton.bmp")
			if not len_verify_button:
				time.sleep(0.5)
				continue

			click(devices, len_verify_button[0], len_verify_button[1], 1)
			break

		time.sleep(3)
		solver_(devices, rok)
	else:
		print("No captcha detected!")


def crop_captcha():
	imagecaptcha = cv2.imread(f"./images/captcha.bmp")
	cropcaptcha = imagecaptcha[100:620, 435:840]
	cv2.imwrite(f"./images/cropcaptcha.jpg", cropcaptcha)


def send_captcha(devices, rok):
	captcha_path = f"./images/cropcaptcha.jpg"
	api_key = "310ec631bdd1f94a868f1805d7bef36c"
	solver = TwoCaptcha(api_key, defaultTimeout=120, pollingInterval=5)

	try:
		print("Send captcha")
		result = solver.coordinates(captcha_path, lang="en")
	except Exception as e:
		print("Lỗi Captcha", e)
		os.system(f"adb -s {devices} shell am force-stop {rok}")
		os.system(f"adb -s {devices} shell am start -n {rok}/com.harry.engine.MainActivity")
		time.sleep(60)
		solver_captcha(devices, rok)
	else:
		print("Giải captcha thành công")
		result_captcha = result
		captcha = result_captcha["code"]
		coordinate = captcha.replace("coordinates:", "").split(";")
		print(coordinate)

		for pair in coordinate:
			x, y = pair.split(",")
			x = x.split("=")[1]
			y = y.split("=")[1]
			os.system(f"adb	-s {devices} shell input tap {int(x) + 435} {int(y) + 100}")
			time.sleep(0.5)
		click(devices, 760, 587, 1)
		time.sleep(1.5)
