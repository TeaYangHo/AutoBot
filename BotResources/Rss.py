from AdbRSS import ADB
import time, AdbRSS
import datetime, threading

def emulator(devices, MEmu, ROK):
	emulator = devices
	adb = ADB(emulator)
	adb.start(MEmu, ROK)
	adb.solver_captcha(ROK)

	Cropland = adb.findCropland
	StoneDeposit = adb.findStoneDeposit
	GoldDeposit = adb.findGoldDeposit

	numberCharacters = 2
	for i in range(numberCharacters):
		adb.screen_capture('ScreenShot.bmp')
		if len(adb.find("ScreenShot.bmp", "AllArmiesBusy.bmp")) > 0:
			print("Các đạo không sẵn sàng")
			if i != numberCharacters - 1:
				adb.changeCharacters(MEmu, ROK)
				adb.solver_captcha(ROK)
			if i == numberCharacters - 1:
				adb.end(MEmu)
		else:
			adb.checkOutCity()
			adb.first(MEmu, ROK, Cropland)
			adb.second(MEmu, ROK, Cropland)
			adb.third(MEmu, ROK, GoldDeposit)
			adb.fourth(MEmu, ROK, GoldDeposit)
			adb.fifth(MEmu, ROK, GoldDeposit)
			adb.solver_captcha(ROK)
			if i != numberCharacters - 1:
				adb.changeCharacters(MEmu, ROK)
				adb.solver_captcha(ROK)
			if i == numberCharacters - 1:
				adb.end(MEmu)
				
def farm():
	while True:
		phut = 60; gio = 60 * phut
		timenow = datetime.datetime.now()
		timenow = timenow.strftime("%d/%m/%Y %H:%M:%S")
		print("Bắt đầu: ", timenow, "\n")

		QT = 'com.lilithgame.roc.gp'
		VN = 'com.rok.gp.vn'

		emulator('127.0.0.1:21503', 'MEmu', QT)
		emulator('127.0.0.1:21523', 'MEmu_2', VN)
		emulator('127.0.0.1:21533', 'MEmu_3', VN)
		timenow = datetime.datetime.now()
		afftertime = timenow + datetime.timedelta(hours=2, minutes = 15)
		afftertime = afftertime.strftime("%d/%m/%Y %H:%M:%S")
		print("Tiếp tục lúc: ", afftertime, "\n")
		time.sleep(2*gio+15*phut)


farm()

# def farm():
# 	def start_emulator(devices, MEmu, ROK):
# 		emulator(devices, MEmu, ROK)
#
# 	while True:
# 		phut = 60
# 		gio = 60 * phut
# 		timenow = datetime.datetime.now()
# 		timenow = timenow.strftime("%d/%m/%Y %H:%M:%S")
# 		print("Bắt đầu:", timenow, "\n")
#
# 		QT = 'com.lilithgame.roc.gp'
# 		VN = 'com.rok.gp.vn'
#
# 		thread_1 = threading.Thread(target=start_emulator, args=('127.0.0.1:21503', 'MEmu', QT))
# 		thread_2 = threading.Thread(target=start_emulator, args=('127.0.0.1:21523', 'MEmu_2', VN))
# 		thread_3 = threading.Thread(target=start_emulator, args=('127.0.0.1:21533', 'MEmu_3', VN))
#
# 		thread_1.start()
# 		thread_2.start()
# 		thread_3.start()
#
# 		thread_1.join()
# 		thread_2.join()
# 		thread_3.join()
#
# 		timenow = datetime.datetime.now()
# 		afftertime = timenow + datetime.timedelta(hours=2, minutes=15)
# 		afftertime = afftertime.strftime("%d/%m/%Y %H:%M:%S")
# 		print("Tiếp tục lúc:", afftertime, "\n")
# 		time.sleep(2 * gio + 15 * phut)
#
# farm()