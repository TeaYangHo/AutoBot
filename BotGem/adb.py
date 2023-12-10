import os
import cv2
import time
import subprocess
import numpy as np
from datetime import datetime
import shutil


def screen_capture(devices, name):
	# command = f"adb -s {devices} exec-out screencap -p > ./images/{name}"
	# try:
	# 	subprocess.run(command, shell=True)
	# except Exception as e:
	# 	print("Error: ", e)
	os.system(f'adb -s {devices} exec-out screencap -p > ./images/{name}')


def click(devices, x, y, timesleep):
	os.system(f"adb	-s {devices} shell input tap {x} {y}")
	time.sleep(timesleep)
	

def back(devices):
	os.system(f"adb	-s {devices} shell input keyevent 4")


def find_template(devices, template):
	screen_capture(devices, f"ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	template = cv2.imread(os.path.join("images", template), cv2.IMREAD_GRAYSCALE)

	result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
	locations = []
	threshold = 0.9
	loc = np.where(result >= threshold)
	if len(loc[0]) > 0:
		for pt in zip(*loc[::-1]):
			locations.append(pt)

	if len(locations) > 0:
		return locations[0]


def find_templates(devices, length, path, templates):
	screen_capture(devices, f"ScreenShot.bmp")
	image = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img = cv2.convertScaleAbs(image)
	locations = []
	threshold = 0.9
	for i in range(1, length + 1):
		template = cv2.imread(os.path.join(f"{path}", f"{templates}{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		template = cv2.convertScaleAbs(template)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			for pt in zip(*loc[::-1]):
				locations.append(pt)

	if len(locations) > 0:
		return locations


def click_templates(devices, templates, sleep):
	screen_capture(devices, f"ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	temp = cv2.imread(os.path.join("images", f"{templates}"), cv2.IMREAD_GRAYSCALE)

	result = cv2.matchTemplate(img_rgb, temp, cv2.TM_CCOEFF_NORMED)
	locations = []
	threshold = 0.9
	loc = np.where(result >= threshold)
	if len(loc[0]) > 0:
		for pt in zip(*loc[::-1]):
			w, h = temp.shape[::-1]
			x = pt[0] + w / 2
			y = pt[1] + h / 2
			locations.append((x, y))
		click(devices, locations[0][0], locations[0][1], sleep)
		return True


def start(devices, rok, index):
	emulator_folder = r"D:\LDPlayer\LDPlayer9"
	print("Start Emulator!")

	command = ["cmd.exe", "/c", f"cd {emulator_folder} && dnconsole.exe launch --index {index}"]
	try:
		subprocess.run(command, shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")

	time.sleep(35)
	print("Start Rise of Kingdoms!")
	os.system(f"adb -s {devices} shell am start -n {rok}/com.harry.engine.MainActivity")
	time.sleep(40)
	check_confirm(devices, rok)


def end(index):
	emulator_folder = r"D:\LDPlayer\LDPlayer9"
	print("Stop Emulator!")
	time.sleep(5)
	command = ["cmd.exe", "/c", f"cd {emulator_folder} && dnconsole.exe quit --index {index}"]
	try:
		subprocess.run(command, shell=True)
	except subprocess.CalledProcessError as e:
		print(f"Error: {e}")
	time.sleep(5)


def start_application(devices, application):
	print("Start application!")
	command = f"adb -s {devices} shell am start -n {application}/com.harry.engine.MainActivity"
	subprocess.run(command, shell=True)
	time.sleep(40)


def end_application(devices, application):
	print("Stop application!")
	command = f"adb -s {devices} shell am force-stop {application}"
	subprocess.run(command, shell=True)
	time.sleep(5)
	
	
def check_confirm(devices, rok):
	confirm_button = find_templates(devices, 3, "images", "ConfirmButton")
	if confirm_button:
		print("Disconnected. Restart!")
		end_application(devices, rok)
		start_application(devices, rok)
	else:
		print("Connected. Continue!")


def check_out_city(devices):
	status = find_template(devices, "OutCity.bmp")
	for i in range(3):
		if not status:
			print("No in the city!")
			break
		else:
			print("In the city. Leave the city!")
			click(devices, 60, 660, 2)
		break


def check_status(devices, rok):
	navigation_bar = find_template(devices, "Navbar.bmp")
	if not navigation_bar:
		date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
		source_path = './images/ScreenShot.bmp'
		destination_path = f'./images/RecycleBin/Status_{date}.bmp'
		shutil.copy(source_path, destination_path)

		print("Abnormal detection. Check status again!")
		end_application(devices, rok)
		start_application(devices, rok)
		check_out_city(devices)
		check_status(devices, rok)
	else:
		print("Not abnormal detection. Continue!")


def search(devices, rok, index, x, y):
	click(devices, 435, 20, 0.5)
	search_button = find_template(devices, 'SearchCoordinate.bmp')
	to_inside_city = find_template(devices, "ToInsideCity.bmp")

	if search_button and to_inside_city:
		print(f"Go to coordinates x:{x} y:{y}")
		click(devices, 635, 145, 0.5)
		os.system(f'adb -s {devices} shell input text "{x}"')
		click(devices, 1200, 670, 0.1)

		click(devices, 790, 145, 0.1)
		os.system(f'adb -s {devices} shell input text "{y}"')
		click(devices, 1200, 670, 0.5)
		click(devices, search_button[0] + 20, search_button[1] + 20, 2.5)

	elif not to_inside_city:
		check_status(devices, rok)
		search(devices, rok, index, x, y)

	else:
		search(devices, rok, index, x, y)


def search_coordinate(devices, rok, index, x, y):
	navbar = find_template(devices, "Navbar.bmp")
	to_inside_city = find_template(devices, "ToInsideCity.bmp")
	if not navbar and to_inside_city:
		click(devices, 640, 360, 1)
		search(devices, rok, index, x, y)
	elif navbar and not to_inside_city:
		check_out_city(devices)
		search(devices, rok, index, x, y)
	elif not navbar and not to_inside_city:
		check_status(devices, rok)
		search_coordinate(devices, rok, index, x, y)
	else:
		search(devices, rok, index, x, y)


def all_armies_busy(devices):
	check_armies_busy = find_templates(devices, 3, "images", "AllArmiesBusy")
	if check_armies_busy:
		print("All Armies Busy!")
		return True
	else:
		print("There is army of unemployed!")
