import random
import cv2
import os
import numpy as np
from adb import screen_capture, back, click, click_templates, find_template, find_templates


def check_point(x, y):
	image = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	if x-150 < 0:
		x = 150
	if y-150 < 0:
		y = 150

	gem_mine = image[y-150:y+150, x-150:x+150]
	img = gem_mine
	locations = []
	threshold = 0.75
	for i in range(1, 110 + 1):
		template = cv2.imread(os.path.join("images/checkGemMine", f"check_gem_mine_{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			for pt in zip(*loc[::-1]):
				locations.append(pt)
	if len(locations) == 0:
		print("Gem mines have no collection troops!")
		return True
	else:
		print("Gem mines have collection troops!")


def check_gem_point(devices):
	screen_capture(devices, f"ScreenShot.bmp")
	image = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	locations = []
	threshold = 0.8

	for i in range(1, 9):
		template = cv2.imread(os.path.join("images/gem", f"Gem{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)

		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			for pt in zip(*loc[::-1]):
				w, h = template.shape[::-1]
				x = pt[0] + w / 2
				y = pt[1] + h / 2
				gem = (x, y)
				locations.append(gem)
	if locations:
		x = int(locations[0][0])
		y = int(locations[0][1])
		if check_point(x, y):
			click(devices, x, y, 0.5)
			return True


def click_gem(devices):
	screen_capture(devices, f"ScreenShot.bmp")
	image = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img = cv2.convertScaleAbs(image)
	locations = []
	threshold = 0.85

	for i in range(1, 8):
		template = cv2.imread(os.path.join("images/gem", f"Gem{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		template = cv2.convertScaleAbs(template)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			for pt in zip(*loc[::-1]):
				w, h = template.shape[::-1]
				x = pt[0] + w / 2
				y = pt[1] + h / 2
				gem = (x, y)
				locations.append(gem)
	if locations:
		click(devices, locations[0][0], locations[0][1], 0.5)
		print("Click", locations[0][0], locations[0][1])


def slot(devices):
	coordinates_slot = [(1105, 260), (1105, 315), (1105, 370), (1105, 425), (1105, 480), (1105, 530)]
	for i in range(6):
		random_slot = random.choice(coordinates_slot)
		click(devices, random_slot[0], random_slot[1], 0.5)
		if find_templates(devices, 6, "images", "Slot"):
			click(devices, 930, 630, 1)
			break
		else:
			coordinates_slot.remove(random_slot)


def gather(devices):
	gather_button = find_template(devices, "GatherButton.bmp")
	if not gather_button:
		click_gem(devices)
		gather(devices)

	click(devices, gather_button[0], gather_button[1], 1.5)

	if not click_templates(devices, "NewTroopButton.bmp", 2):
		back(devices)
		return
	slot(devices)
