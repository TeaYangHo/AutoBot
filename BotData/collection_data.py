import time
import cv2
import os
import pyperclip
import io
import datetime
import numpy as np


starttime = datetime.datetime.now().strftime("%d_%m")
folder_path = f"Data/Data_{starttime}"


def create_folder():
	try:
		path = folder_path
		os.makedirs(folder_path)
		os.makedirs(path+"/GovernorProfile")
		os.makedirs(path + "/MoreInfo")
		print(f"Thư mục đã được tạo. Dữ liệu được lưu ở file {folder_path}")
	except FileExistsError:
		print(f"Thư mục đã tồn tại.")


def screen_capture(devices, name):
	os.system(f"adb -s {devices} exec-out screencap -p > ./images/{name}")


def click_template(devices, template, timesleep):
	screen_capture(devices, "ScreenShot.bmp")
	img = cv2.imread(os.path.join("images", "ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img_gray = cv2.convertScaleAbs(img)

	template = cv2.imread(os.path.join("images", template), cv2.IMREAD_GRAYSCALE)
	template = cv2.convertScaleAbs(template)

	result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
	threshold = 0.95

	locations = np.where(result >= threshold)
	if len(locations[0]) > 0:
		x, y = int(np.mean(locations[1])), int(np.mean(locations[0]))
		w, h = template.shape[::-1]
		x_image = x + w / 2
		y_image = y + h / 2
		os.system(f"adb	-s {devices} shell input tap {x_image} {y_image}")
	time.sleep(timesleep)


def find(devices, template):
	screen_capture(devices, "ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", "ScreenShot.bmp"))
	template = cv2.imread(os.path.join("images", template))

	result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
	locations = []
	threshold = 0.85
	loc = np.where(result >= threshold)
	if len(loc[0]) > 0:
		for pt in zip(*loc[::-1]):
			locations.append(pt)
	if len(locations) > 0:
		return True


def click(devices, x, y, timesleep):
	os.system(f"adb	-s {devices} shell input tap {x} {y}")
	time.sleep(timesleep)


def start():
	devices = "127.0.0.1:21533"  # 127.0.0.1:21533
	top_bxh = 305
	name_data = []

	start_time = datetime.datetime.now()
	start_time = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
	print("Bắt đầu thu thập dữ liệu - ", start_time)

	create_folder()
	for top in range(1, top_bxh + 1):
		if top < 4:
			temp_top = f"top{top}.bmp"
			click_template(devices, temp_top, 2)
		else:
			click(devices, 180, 485, 2)

		find_profile = find(devices, "check_governor_profile.bmp")
		if not find_profile:
			print(f"Không xem được profile top {top}. Loại bỏ và kiểm tra lại sau")
			click(devices, 305, 570, 2)

		find_profile = find(devices, "check_governor_profile.bmp")
		if not find_profile:
			print(f"Không xem được profile top {top}. Loại bỏ và kiểm tra lại sau")
			click(devices, 305, 650, 2)

		click(devices, 895, 250, 1)
		tktd = find(devices, "kill_statistics.bmp")
		if tktd:
			os.system(f"adb -s {devices} exec-out screencap -p > ./{folder_path}/GovernorProfile/governorprofile{top}.bmp")
		else:
			click(devices, 895, 250, 1)
			os.system(f"adb -s {devices} exec-out screencap -p > ./{folder_path}/GovernorProfile/governorprofile{top}.bmp")

		click(devices, 285, 590, 1)
		tktc = find(devices, "battle_statistics.bmp")
		if tktc > 0:
			os.system(f"adb -s {devices} exec-out screencap -p > ./{folder_path}/MoreInfo/moreinfo{top}.bmp")
		else:
			click(devices, 285, 590, 1)
			os.system(f"adb -s {devices} exec-out screencap -p > ./{folder_path}/MoreInfo/moreinfo{top}.bmp")

		click(devices, 300, 125, 1)
		name_governor = pyperclip.paste()
		if name_governor in name_data:
			print("Trùng tên, kiểm tra lại top: ", top)
			break
		else:
			name_data.append(name_governor)
		time.sleep(1)

		click(devices, 1115, 45, 1)
		click(devices, 1090, 80, 1)

		with io.open(f"{folder_path}/Data_{starttime}_Name.txt", "w", encoding="utf-8") as file:
			for name in name_data:
				file.write(name + "\n")
		print(f"Hoàn thành thu thập dữ liệu top {top}")

	end_time = datetime.datetime.now()
	end_time = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
	print("Hoàn thành thu thập dữ liệu - ", end_time)

	running_time = end_time - start_time
	running_time = datetime.timedelta(seconds=running_time.seconds)
	print("Thời gian thực hiện - ", running_time)


start()
