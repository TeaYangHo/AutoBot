import cv2
import os
import numpy as np
from adb import screen_capture, click, back
from find import find_template, click_gem, click_templates


def find_home(devices):
	screen_capture(devices, "ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", "ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img = img_rgb[200:430, 1180:1270]

	locations = []
	threshold = 0.8

	for i in range(1, 3):
		template = cv2.imread(os.path.join("images", f"ArmyHome{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
		loc = np.where(result >= threshold)

		if loc[0].size > 0:
			for pt in zip(*loc[::-1]):
				x, y = pt[0] + 1180, pt[1] + 200
				locations.append((x, y))

	if len(locations) > 0:
		return locations[0]


def find_returning(devices):
	screen_capture(devices, "ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", "ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img = img_rgb[200:430, 1180:1270]

	locations = []
	threshold = 0.8

	for i in range(1, 3):
		template = cv2.imread(os.path.join("images", f"ArmyReturning{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
		loc = np.where(result >= threshold)

		if loc[0].size > 0:
			for pt in zip(*loc[::-1]):
				x, y = pt[0] + 1180, pt[1] + 200
				locations.append((x, y))

	if len(locations) > 0:
		return locations[0]


def crop_commander_home(locations):
	image = cv2.imread(os.path.join("images", "ScreenShot.bmp"))
	y1 = int(locations[1] - 40)
	y2 = int(locations[1] - 5)
	x1 = int(locations[0] - 45)
	x2 = int(locations[0] + 15)
	crop_image = image[y1:y2, x1:x2]
	commander_image = crop_image
	cv2.imwrite('images/Commander.bmp', commander_image)

	img_commander = cv2.imread(os.path.join("images", "Commander.bmp"), cv2.IMREAD_GRAYSCALE)
	img = cv2.convertScaleAbs(img_commander)
	threshold = 0.8
	for i in range(1, 6 + 1):
		template = cv2.imread(os.path.join("images/commander", f"Commander{i}.bmp"), cv2.IMREAD_GRAYSCALE)
		template = cv2.convertScaleAbs(template)
		result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
		loc = np.where(result >= threshold)
		if len(loc[0]) > 0:
			return i


def commander_unemployed(locations):
	commander = crop_commander_home(locations)
	if commander == 1:
		print("Joan is unemployed!")
		return "Joan"

	elif commander == 2:
		print("Tamar is unemployed!")
		return "Tamar"

	elif commander == 3:
		print("Gaius is unemployed!")
		return "Gaius"

	elif commander == 4:
		print("Matilda is unemployed!")
		return "Matilda"

	elif commander == 5:
		print("Constance is unemployed!")
		return "Constance"

	elif commander == 6:
		print("Sarka is unemployed!")
		return "Sarka"


def click_commander(devices, commander):
	screen_capture(devices, f"ScreenShot.bmp")
	img_rgb = cv2.imread(os.path.join("images", f"ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	template = cv2.imread(os.path.join("images/commander/5armies", f"{commander}.bmp"), cv2.IMREAD_GRAYSCALE)

	result = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
	locations = []
	threshold = 0.85
	loc = np.where(result >= threshold)
	if len(loc[0]) > 0:
		for pt in zip(*loc[::-1]):
			w, h = template.shape[::-1]
			x = pt[0] + w / 2
			y = pt[1] + h / 2
			locations.append((x, y))
		click(devices, locations[0][0], locations[0][1], 0.5)
		return True
	else:
		back(devices)


def gather_commander(devices, commander):
	gather_button = find_template(devices, "GatherButton.bmp")
	if not gather_button:
		click_gem(devices)
		gather_commander(devices, commander)

	click(devices, gather_button[0], gather_button[1], 1.5)
	click_commander(devices, commander)
	click_templates(devices, "MarchButton.bmp", 0.5)
	for i in range(5):
		march_button = find_template(devices, "MarchButton.bmp")
		if not march_button:
			break
		click(devices, march_button[0], march_button[1], 0.5)
