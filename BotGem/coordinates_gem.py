import cv2
import math
import os
import sqlite3
import pytesseract
from adb import screen_capture, click, back
from count_coordinates import gem_in_zone_gorlitz, gem_in_zone_vigo


def convert_coordinates(coordinates):
	x_value = ""
	y_value = ""
	parts = coordinates

	try:
		parts = parts.replace(":", "").replace(".", "").replace("¥", "Y").replace("V", "Y")
		parts = parts.split()
		for part in parts:
			if part.startswith("X"):
				if "Y" in part:
					x, y = part.split("Y")
					x_value = x[1:]
					y_value = y
				else:
					x_value = part[1:]

			elif "X" in part and "Y" not in part:
				server, x = part.split("X")
				x_value = x

			elif "X" in part and "Y" in part:
				x, y = part.split("Y")
				server, x = x.split("X")
				x_value = x
				y_value = y

			elif part.startswith("Y"):
				y_value = part[1:]

		x_value = int(x_value)
		y_value = int(y_value)

	except Exception as e:
		print("Error: ", e)

	return x_value, y_value


def extract(image, coordinates):
	x1, y1, x2, y2 = coordinates
	ext_image = image[y1:y2, x1:x2]

	threshold = cv2.threshold(ext_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
	text = pytesseract.image_to_string(threshold, config=r"--oem 3 --psm 11")
	x, y = convert_coordinates(text)

	if isinstance(x and y, int):
		return x, y
	else:
		data_extract = []
		for i in range(115, 121):
			threshold = cv2.threshold(ext_image, i, 255, cv2.THRESH_BINARY_INV)[1]
			text = pytesseract.image_to_string(threshold, config=r"--oem 3 --psm 11")
			data_extract.append(text)
		common_number = max(set(data_extract), key=data_extract.count)
		x, y = convert_coordinates(common_number)
		return x, y


def extract_coordinates_commander(devices):
	extract_coordinate = (260, 0, 432, 43)
	click(devices, 1190, 180, 1.5)

	screen_capture(devices, "Screenshot.bmp")
	img_rgb = cv2.imread(os.path.join("images", "Screenshot.bmp"), cv2.IMREAD_GRAYSCALE)
	x, y = extract(img_rgb, extract_coordinate)
	print(f"Results of extracting coordinates X:{x} Y:{y}")
	back(devices)
	return x, y


def start_calculate(gem_coordinates, x_commander, y_commander):
	nearest_distance = float('inf')
	nearest_coordinates = None
	for id_gem, x_gem, y_gem in gem_coordinates:
		distance = calculate_distance(x_commander, y_commander, x_gem, y_gem)
		if distance < nearest_distance:
			nearest_distance = distance
			nearest_coordinates = (id_gem, x_gem, y_gem)
	return nearest_coordinates


def calculate_distance(x1, y1, x2, y2):
	return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def find_nearest_gem_mine_2589(x_commander, y_commander):
	_LINK_DB = r"D:/Code Python/BotGEM_V2/coordinate.db"
	sqlite_connection = sqlite3.connect(_LINK_DB)
	cursor = sqlite_connection.cursor()


	nearest_coordinates = None
	gorlitz_1 = (376 <= x_commander <= 495) and (230 <= y_commander <= 260)
	gorlitz_2 = (315 <= x_commander <= 734) and (260 <= y_commander <= 312)
	gorlitz_3 = (315 <= x_commander <= 702) and (312 <= y_commander <= 341)
	gorlitz_4 = (315 <= x_commander <= 673) and (341 <= y_commander <= 372)
	gorlitz_5 = (315 <= x_commander <= 645) and (372 <= y_commander <= 404)
	gorlitz_6 = (315 <= x_commander <= 582) and (404 <= y_commander <= 433)
	gorlitz_7 = (286 <= x_commander <= 492) and (433 <= y_commander <= 442)
	gorlitz_8 = (286 <= x_commander <= 492) and (442 <= y_commander <= 472)
	gorlitz_9 = (258 <= x_commander <= 492) and (472 <= y_commander <= 493)
	gorlitz_10 = (258 <= x_commander <= 463) and (493 <= y_commander <= 516)
	gorlitz_11 = (285 <= x_commander <= 463) and (516 <= y_commander <= 550)
	gorlitz_12 = (285 <= x_commander <= 434) and (550 <= y_commander <= 584)

	vigo_1 = (496 <= x_commander <= 732) and (438 <= y_commander <= 673)
	vigo_2 = (585 <= x_commander <= 641) and (410 <= y_commander <= 438)
	vigo_3 = (732 <= x_commander <= 762) and (528 <= y_commander <= 612)
	vigo_4 = (526 <= x_commander <= 673) and (673 <= y_commander <= 705)
	vigo_5 = (526 <= x_commander <= 582) and (705 <= y_commander <= 732)
	vigo_6 = (466 <= x_commander <= 496) and (500 <= y_commander <= 673)
	vigo_7 = (438 <= x_commander <= 466) and (560 <= y_commander <= 673)

	gorlitz = gorlitz_1 or gorlitz_2 or gorlitz_3 or gorlitz_4 or gorlitz_5 or gorlitz_6 or gorlitz_7 or gorlitz_8 or gorlitz_9 or gorlitz_10 or gorlitz_11 or gorlitz_12
	vigo = vigo_1 or vigo_2 or vigo_3 or vigo_4 or vigo_5 or vigo_6 or vigo_7

	if gorlitz:
		gem_coordinates = cursor.execute(gem_in_zone_gorlitz).fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)
		# else:
		# 	gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		# 	if gem_coordinates:
		# 		nearest_coordinates = start_calculate(gem_coordinates, 800, 496)  # pass 5 green

	elif vigo:
		gem_coordinates = cursor.execute(gem_in_zone_vigo).fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)
		# else:
		# 	gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		# 	if gem_coordinates:
		# 		nearest_coordinates = start_calculate(gem_coordinates, 736, 404)  # pass 5 blue
	else:
		gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)

	if nearest_coordinates:
		delete_query = "DELETE FROM COORDINATE WHERE id = ?"
		print(f"Delete coordinates X:{nearest_coordinates[1]} Y:{nearest_coordinates[2]} from database")
		cursor.execute(delete_query, (nearest_coordinates[0],))

		coordinate = (nearest_coordinates[1], nearest_coordinates[2])
		sqlite_connection.commit()
		cursor.close()
		sqlite_connection.close()
		return coordinate


def find_nearest_gem_mine_c11987(x_commander, y_commander):
	_LINK_DB = r"D:/Code Python/BotGEM_V2/coordinate.db"
	sqlite_connection = sqlite3.connect(_LINK_DB)
	cursor = sqlite_connection.cursor()

	gem_in_zone_5_blue = """
	SELECT id, X, Y
	FROM COORDINATE
	WHERE ((X >= 672 AND X <= 793 AND Y >= 375 AND Y <= 404) OR
			(X >= 555 AND X <= 885 AND Y >= 193 AND Y <= 375) OR
			(X >= 555 AND X <= 855 AND Y >= 165 AND Y <= 193) OR
			(X >= 644 AND X <= 855 AND Y >= 136 AND Y <= 165))
	"""

	gem_in_zone_5_green = """
	SELECT id, X, Y
	FROM COORDINATE
	WHERE ((X >= 890 AND X <= 972 AND Y >= 260 AND Y <= 317) OR
			(X >= 890 AND X <= 1066 AND Y >= 317 AND Y <= 383) OR
			(X >= 800 AND X <= 1092 AND Y >= 383 AND Y <= 463) OR
			(X >= 800 AND X <= 1035 AND Y >= 463 AND Y <= 494) OR
			(X >= 860 AND X <= 1035 AND Y >= 494 AND Y <= 587) OR
			(X >= 830 AND X <= 1001 AND Y >= 587 AND Y <= 700))
	"""

	nearest_coordinates = None

	blue_1 = 672 <= x_commander <= 793 and 375 <= y_commander <= 404
	blue_2 = 555 <= x_commander <= 885 and 193 <= y_commander <= 375
	blue_3 = 555 <= x_commander <= 855 and 165 <= y_commander <= 193
	blue_4 = 644 <= x_commander <= 855 and 136 <= y_commander <= 165

	green_1 = 890 <= x_commander <= 972 and 260 <= y_commander <= 317
	green_2 = 890 <= x_commander <= 1066 and 317 <= y_commander <= 383
	green_3 = 800 <= x_commander <= 1092 and 383 <= y_commander <= 463
	green_4 = 800 <= x_commander <= 1035 and 463 <= y_commander <= 494
	green_5 = 860 <= x_commander <= 1035 and 494 <= y_commander <= 587
	green_6 = 830 <= x_commander <= 1001 and 587 <= y_commander <= 700

	zone_5_blue = blue_1 or blue_2 or blue_3 or blue_4
	zone_5_green = green_1 or green_2 or green_3 or green_4 or green_5 or green_6

	if zone_5_blue:
		gem_coordinates = cursor.execute(gem_in_zone_5_blue).fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)
		# else:
		# 	gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		# 	if gem_coordinates:
		# 		nearest_coordinates = start_calculate(gem_coordinates, 800, 496)  # pass 5 green

	elif zone_5_green:
		gem_coordinates = cursor.execute(gem_in_zone_5_green).fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)
		# else:
		# 	gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		# 	if gem_coordinates:
		# 		nearest_coordinates = start_calculate(gem_coordinates, 736, 404)  # pass 5 blue
	else:
		gem_coordinates = cursor.execute("SELECT id, X, Y FROM COORDINATE").fetchall()
		if gem_coordinates:
			nearest_coordinates = start_calculate(gem_coordinates, x_commander, y_commander)

	if nearest_coordinates:
		delete_query = "DELETE FROM COORDINATE WHERE id = ?"
		print(f"Delete coordinates X:{nearest_coordinates[1]} Y:{nearest_coordinates[2]} from database")
		cursor.execute(delete_query, (nearest_coordinates[0],))

		coordinate = (nearest_coordinates[1], nearest_coordinates[2])
		sqlite_connection.commit()
		cursor.close()
		sqlite_connection.close()
		return coordinate
