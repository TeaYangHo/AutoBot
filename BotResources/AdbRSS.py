import os, cv2, time, subprocess, sys
import numpy as np
from twocaptcha import TwoCaptcha

class ADB():
	def __init__(self, emulator):
		self.emulator = emulator

	def screen_capture(self, name):
		os.system(f'adb -s {self.emulator} exec-out screencap -p > ./images/{name}')

	def click(self, x, y):
		os.system(f'adb	-s {self.emulator} shell input tap {x} {y}')

	def back(self):
		os.system(f'adb	-s {self.emulator} shell input keyevent 4')

	def click_template(self, screenshot, template):
		img = cv2.imread(os.path.join('images', screenshot), cv2.IMREAD_GRAYSCALE)
		img_gray = cv2.convertScaleAbs(img)

		template = cv2.imread(os.path.join('images', template), cv2.IMREAD_GRAYSCALE)
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

	def find(self, screenshot, template):
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
	def solver_captcha(self, ROK):
		for i in range(2):
			self.screen_capture('captcha.bmp')
			lenCaptcha1 = self.find('captcha.bmp', 'CaptchaAppearIcon1.bmp')
			lenCaptcha2 = self.find('captcha.bmp', 'CaptchaAppearIcon2.bmp')
			if len(lenCaptcha1) > 0 or len(lenCaptcha2) > 0:
				print("Phát hiện captcha. Giải captcha")
				if len(lenCaptcha1) > 0:
					self.click(lenCaptcha1[0][0], lenCaptcha1[0][1])
				if len(lenCaptcha2) > 0:
					self.click(lenCaptcha2[0][0], lenCaptcha2[0][1])
				time.sleep(3)
				for count in range(10):
					self.screen_capture('captcha.bmp')
					lenVerifyButton = self.find('captcha.bmp', 'VerifyButton.bmp')
					if len(lenVerifyButton) > 0:
						self.click_template('captcha.bmp', 'VerifyButton.bmp')
						break
					elif len(lenVerifyButton) == 0:
						time.sleep(1)

				time.sleep(5)
				for count in range(5):
					self.screen_capture('captcha.bmp')
					lenCaptchaShow = self.find('captcha.bmp', 'CaptchaShow.bmp')
					if len(lenCaptchaShow) > 0:
						time.sleep(5)
						self.crop_captcha()
						self.send_captcha(ROK)
						self.screen_capture('captcha.bmp')
						lenCheckCaptcha = self.find('captcha.bmp', 'CheckCaptcha.bmp')
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

	def crop_captcha(self):
		imagecaptcha = cv2.imread('./images/captcha.bmp')
		cropcaptcha = imagecaptcha[100:620, 435:840]
		cv2.imwrite('./images/cropcaptcha.jpg', cropcaptcha)

	def send_captcha(self, ROK):
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
			self.solver_captcha(ROK)
		else:
			print("Giải captcha thành công")
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
			self.click(760, 587)
			time.sleep(5)

	def checkResourceMine(self, screenshot):
		image = cv2.imread(os.path.join('images', screenshot))
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
			result = cv2.matchTemplate(img , template, cv2.TM_CCOEFF_NORMED)

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
		self.screen_capture("ScreenShot.bmp")
		if len(self.find('ScreenShot.bmp', 'ConfirmButton.bmp')) == 0 or len(self.find('ScreenShot.bmp', 'ConfirmButton2.bmp')) == 0:
			print("Hoạt động bình thường")
		else:
			print("Mất kết nối. Khởi động lại")
			self.end(MEmu)
			self.start(MEmu, ROK)

	def checkOutCity(self):
		for i in range(3):
			self.screen_capture("ScreenShot.bmp")
			if len(self.find('ScreenShot.bmp', 'OutCity.bmp')) == 0:
				print("Không quan sát ở trong thành phố")
				break
			elif len(self.find('ScreenShot.bmp', 'OutCity.bmp')) > 0:
				print("Đang quan sát ở trong thành phố")
				print("Rời khỏi và thu thập tài nguyên")
				self.click(60, 660)
				time.sleep(2)
			break

	def findCropland(self):
		print("Thu thập Ngô")
		self.click(60, 540)
		time.sleep(1)
		self.click(451, 636)
		self.click(447, 491)
		time.sleep(3)

	def findStoneDeposit(self):
		print("Thu thập Đá")
		self.click(60, 540)
		time.sleep(1)
		self.click(834, 636)
		self.click(830, 492)
		time.sleep(3)

	def findGoldDeposit(self):
		print("Thu thập Vàng")
		#self.click(60, 540)
		self.screen_capture('ScreenShot.bmp')
		self.click_template('ScreenShot.bmp', "SearchButton.bmp")
		time.sleep(1)
		self.click(1020, 640)
		self.click(1020, 490)
		time.sleep(3)

	def check_app_running(self, ROK):
		output = subprocess.check_output(['adb', '-s', self.emulator, 'shell', 'dumpsys', 'window', 'windows'])
		output_str = output.decode()
		if ROK in output_str:
			print(f"{ROK} đang hoạt động.")
		else:
			print("Rise of Kingdoms không hoạt động. Khởi động Rise of Kingdoms")
			os.system(f'adb -s {self.emulator} shell am start -n {ROK}/com.harry.engine.MainActivity')
			time.sleep(60)

	def checkStatus(self, MEmu, ROK):
		self.checkConfirm(MEmu, ROK)
		self.screen_capture("ScreenShot.bmp")
		ToInsideCity = self.find("ScreenShot.bmp", "ToInsideCity.bmp")
		if len(ToInsideCity) > 0:
			print("Trạng thái bình thường")
		else:
			print("Phát hiện bất thường. Kiểm tra lại trạng thái!")
			for i in range(5):
				self.back()
				time.sleep(1)
				self.screen_capture("ScreenShot.bmp")
				Calcel = self.find("ScreenShot.bmp", "CalcelButton.bmp")
				if len(Calcel) > 0:
					self.click(Calcel[0][0], Calcel[0][1])
					time.sleep(1)
					self.checkOutCity()
					break
				else:
					self.back()
				if i == 4:
					print("Rise of Kingdoms không hoạt động. Khởi động Rise of Kingdoms")
					os.system(f'adb -s {self.emulator} shell am force-stop {ROK}')
					time.sleep(5)
					os.system(f'adb -s {self.emulator} shell am start -n {ROK}/com.harry.engine.MainActivity')
					time.sleep(60)

	def gather(self, MEmu, ROK, Resources):
		self.click(640, 360)
		time.sleep(1)
		self.screen_capture('ScreenShot.bmp')
		GatherButton = self.find('ScreenShot.bmp', 'GatherButton.bmp')
		RecallButton = self.find('ScreenShot.bmp', 'RecallButton.bmp')
		if len(GatherButton) > 0 and len(RecallButton) == 0:
			self.click(GatherButton[0][0], GatherButton[0][1])
		else:
			self.checkStatus(MEmu, ROK)
			Resources()
			self.gather(MEmu, ROK, Resources)
		time.sleep(2)
		self.click(1010, 145)
		time.sleep(3)

	def first(self, MEmu, ROK, Resources):
		print("\nĐạo quân đầu tiên")
		self.checkConfirm(MEmu, ROK)
		for i in range(6):
			self.screen_capture('ScreenShot.bmp')
			if len(self.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
				break
			else:
				Resources()
				# self.findCropland()
				self.screen_capture('ScreenShot.bmp')
				if len(self.checkResourceMine('ScreenShot.bmp')) > 0:
					print("Mỏ tài nguyên đang có quân đến thu thập")
					print("Tìm kiếm mỏ tiếp theo")
				else:
					print("Mỏ tài nguyên không có quân đến thu thập")
					self.gather(MEmu, ROK, Resources)
					self.click(1100, 290)
					time.sleep(1)
					self.screen_capture('ScreenShot.bmp')
					if len(self.find('ScreenShot.bmp', 'Slot1.bmp')) > 0:
						print("Đạo quân sẵn sàng")
						self.click(930, 630)
					else:
						print("Đạo quân không ở trong thành phố")
						self.click(1110, 40)
					break
		time.sleep(2)

	def second(self, MEmu, ROK, Resources):
		print("\nĐạo quân thứ hai")
		self.checkConfirm(MEmu, ROK)
		for i in range(6):
			self.screen_capture('ScreenShot.bmp')
			if len(self.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
				break
			else:
				Resources()
				#self.findStoneDeposit()
				self.screen_capture('ScreenShot.bmp')
				if len(self.checkResourceMine('ScreenShot.bmp')) > 0:
					print("Mỏ tài nguyên đang có quân đến thu thập")
					print("Tìm kiếm mỏ tiếp theo")
				else:
					print("Mỏ tài nguyên không có quân đến thu thập")
					self.gather(MEmu, ROK, Resources)
					self.click(1100, 350)
					time.sleep(1)
					self.screen_capture('ScreenShot.bmp')
					if len(self.find('ScreenShot.bmp', 'Slot2.bmp')) > 0:
						print("Đạo quân sẵn sàng")
						self.click(930, 630)
					else:
						print("Đạo quân không ở trong thành phố")
						self.click(1110, 40)
					break
		time.sleep(2)

	def third(self, MEmu, ROK, Resources):
		print("\nĐạo quân thứ ba")
		self.checkConfirm(MEmu, ROK)
		for i in range(6):
			self.screen_capture('ScreenShot.bmp')
			if len(self.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
				break
			else:
				Resources()
				#self.findGoldDeposit()
				self.screen_capture('ScreenShot.bmp')
				if len(self.checkResourceMine('ScreenShot.bmp')) > 0:
					print("Mỏ tài nguyên đang có quân đến thu thập")
					print("Tìm kiếm mỏ tiếp theo")
				else:
					print("Mỏ tài nguyên không có quân đến thu thập")
					self.gather(MEmu, ROK, Resources)
					self.click(1100, 410)
					time.sleep(1)
					self.screen_capture('ScreenShot.bmp')
					if len(self.find('ScreenShot.bmp', 'Slot3.bmp')) > 0:
						print("Đạo quân sẵn sàng")
						self.click(930, 630)
					else:
						print("Đạo quân không ở trong thành phố")
						self.click(1110, 40)
					break
		time.sleep(2)

	def fourth(self, MEmu, ROK, Resources):
		print("\nĐạo quân thứ tư")
		self.checkConfirm(MEmu, ROK)
		for i in range(6):
			self.screen_capture('ScreenShot.bmp')
			if len(self.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
				break
			else:
				Resources()
				#self.findGoldDeposit()
				self.screen_capture('ScreenShot.bmp')
				if len(self.checkResourceMine('ScreenShot.bmp')) > 0:
					print("Mỏ tài nguyên đang có quân đến thu thập")
					print("Tìm kiếm mỏ tiếp theo")
				else:
					print("Mỏ tài nguyên không có quân đến thu thập")
					self.gather(MEmu, ROK, Resources)
					self.click(1100, 470)
					time.sleep(1)
					self.screen_capture('ScreenShot.bmp')
					if len(self.find('ScreenShot.bmp', 'Slot4.bmp')) > 0:
						print("Đạo quân sẵn sàng")
						self.click(930, 630)
					else:
						print("Đạo quân không ở trong thành phố")
						self.click(1110, 40)
					break
		time.sleep(2)

	def fifth(self, MEmu, ROK, Resources):
		print("\nĐạo quân thứ năm")
		self.checkConfirm(MEmu, ROK)
		for i in range(6):
			self.screen_capture('ScreenShot.bmp')
			if len(self.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
				break
			else:
				Resources()
				#self.findGoldDeposit()
				self.screen_capture('ScreenShot.bmp')
				if len(self.checkResourceMine('ScreenShot.bmp')) > 0:
					print("Mỏ tài nguyên đang có quân đến thu thập")
					print("Tìm kiếm mỏ tiếp theo")
				else:
					print("Mỏ tài nguyên không có quân đến thu thập")
					self.gather(MEmu, ROK, Resources)
					self.click(1100, 530)
					time.sleep(1)
					self.screen_capture('ScreenShot.bmp')
					if len(self.find('ScreenShot.bmp', 'Slot5.bmp')) > 0:
						print("Đạo quân sẵn sàng")
						self.click(930, 630)
					else:
						print("Đạo quân không ở trong thành phố")
						self.click(1110, 40)
					break
		time.sleep(2)

	def checkCharacters(self, screenshot, MEmu, ROK):
		image = cv2.imread(os.path.join('images', screenshot))
		number_images = 2
		clicked = [False] * number_images
		for i in range(number_images):
			x_start = 180 + (i % 2) * 470
			x_end = 630 + (i % 2) * 470
			y_start = 210 + (i // 2) * 135
			y_end = y_start + 115
			characters = image[y_start:y_end, x_start:x_end]
			cv2.imwrite(f"./images/Characters{i + 1}.bmp", characters)

		for i in range(number_images):
			x_start = 180 + (i % 2) * 470
			x_end = 630 + (i % 2) * 470
			y_start = 210 + (i // 2) * 135
			y_end = y_start + 115
			image = cv2.imread(os.path.join('images', f"Characters{i + 1}.bmp"))
			template = cv2.imread(os.path.join('images', 'MainChecked.bmp'))
			threshold = 0.8
			result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

			loc = np.where(result >= threshold)
			if len(loc[0]) > 0:
				clicked[i] = True
			else:
				self.click(x_start + (x_end - x_start) // 2, y_start + (y_end - y_start) // 2)
				time.sleep(2)
				self.click(815, 515), self.click(815, 515)
				time.sleep(60)
				self.checkConfirm(MEmu, ROK)
				clicked[i] = True

	def changeCharacters(self, MEmu, ROK):
		print("Thay đổi nhân vật")
		self.click(50, 40)
		time.sleep(1)
		self.click( 990, 530)
		time.sleep(1)
		self.click( 350, 370)
		time.sleep(5)
		self.screen_capture('ScreenShot.bmp')
		self.checkCharacters('ScreenShot.bmp', MEmu, ROK)

	# def inputtext(self, text):
	# 	for i in text:
	# 		if i.isdigit():
	# 			continue
	# 		else:
	# 			os.system(f"adb -s {self.emulator} shell input text '{i}'")
	#
	# 	os.system(f"adb -s {self.emulator} shell input keyevent 19")
	# 	for i in text:
	# 		if i.isdigit():
	# 			os.system(f"adb -s {self.emulator} shell input text '{i}'")
	# 		else:
	# 			os.system(f"adb -s {self.emulator} shell input keyevent 22")
	#
	# def changeAccount(self):
	# 	print("Thay đổi tài khoản")
	# 	with open("account.txt", "r") as f:
	# 		accounts = [line.strip().split("|") for line in f.readlines()]
	# 	for i, account in enumerate(accounts):
	# 		self.click(50, 40)
	# 		time.sleep(1)
	# 		self.click(990, 530)
	# 		time.sleep(1)
	# 		self.click(540, 370)
	# 		time.sleep(3)
	# 		self.click(1150, 45)
	# 		time.sleep(1)
	#
	# 		self.inputtext(account[0])
	# 		time.sleep(1)
	# 		self.click(650, 340)
	# 		time.sleep(2)
	# 		self.click(970, 405)
	# 		time.sleep(1)
	# 		self.click(265, 340)
	# 		time.sleep(1)
	# 		self.inputtext(account[1])
	# 		self.click(630, 490)
	# 		time.sleep(45)


if __name__ == '__main__':
	emulator = '127.0.0.1:21513'
	QT = 'com.lilithgame.roc.gp'
	VN = 'com.rok.gp.vn'
	adb = ADB(emulator)
	#adb.screen_capture('ScreenShot.bmp')
	#Cropland = adb.findCropland()
	# modify the following line to choose the desired resource function
	adb.checkStatus('MEmu_1', VN)
	#os.system(f'adb -s {emulator} shell am force-stop {VN}')


