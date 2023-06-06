import time, cv2, pytesseract, os, pyperclip, io
import pandas as pd
import numpy as np

id = (510, 175, 735, 215)
name = (510, 207, 790, 255)
t1 = (690, 365, 900, 400)
t2 = (690, 400, 900, 435)
t3 = (690, 435, 900, 470)
t4 = (690, 470, 900, 505)
t5 = (690, 505, 900, 540)
prof = [id, name, t5, t4, t3, t2, t1]

killpoint = (875, 95, 1120, 155)
power = (650, 95, 795, 155)
dead = (900, 350, 1065, 395)
resource = (900, 532, 1065, 578)
infor = [killpoint, power, dead, resource]

governor = []
name_data = []

def screen_capture(emulator, name):
	os.system(f'adb -s {emulator} exec-out screencap -p > ./images/{name}')

def click_template(emulator, template):
	screen_capture(emulator, "ScreenShot.bmp")
	img = cv2.imread(os.path.join('images', "ScreenShot.bmp"), cv2.IMREAD_GRAYSCALE)
	img_gray = cv2.convertScaleAbs(img)

	template = cv2.imread(os.path.join('images', template), cv2.IMREAD_GRAYSCALE)
	template = cv2.convertScaleAbs(template)

	result = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
	threshold = 0.95

	locations = np.where(result >= threshold)
	if len(locations[0]) > 0:
		x, y = int(np.mean(locations[1])), int(np.mean(locations[0]))
		w, h = template.shape[::-1]
		x_image = x + w / 2
		y_image = y + h / 2
		os.system(f'adb	-s {emulator} shell input tap {x_image} {y_image}')

def click(emulator, x, y):
	os.system(f"adb	-s {emulator} shell input tap {x} {y}")

def screnGOVERNOR(emulator, topBXH):
	i = 1
	temp_copy = "CopyName.bmp"
	temp_top = f"top{i}.bmp"
	for img in range(topBXH):
		if i <= 4:
			temp_top = f"top{i}.bmp"
			click_template(emulator, temp_top)
		else:
			click(emulator, 180, 485)
		time.sleep(3)

		click_template(emulator, temp_copy)
		time.sleep(1)
		name = pyperclip.paste()
		if name in name_data:
			click(emulator, 1115, 45)
			click_template(emulator, temp_top)
			click_template(emulator, temp_copy)
			name = pyperclip.paste()
			time.sleep(1)
			name_data.append(name)
		else:
			name_data.append(name)
		time.sleep(1)

		click(emulator, 895, 285)
		time.sleep(2)
		os.system(f"adb -s {emulator} exec-out screencap -p > ./GovernorProfile/governorprofile{i}.bmp")
		time.sleep(1)

		click(emulator, 305, 535)
		time.sleep(2)
		os.system(f"adb -s {emulator} exec-out screencap -p > ./MoreInfo/moreinfo{i}.bmp")
		time.sleep(1)

		click(emulator, 1115, 45)
		time.sleep(1)
		click(emulator, 1090, 80)
		time.sleep(1)
		i += 1

	with io.open('name1.txt', 'w', encoding='utf-8') as file:
		for name in name_data:
			file.write(name + '\n')

def extract_image(image, coordinate):
	pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
	x, y, w, h = coordinate
	ext_image = image[y:h, x:w, 1]
	threshold = cv2.threshold(ext_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
	extracted_text = pytesseract.image_to_string(threshold, lang="eng+vie", config="--oem 3 --psm 6")
	return extracted_text.strip()

def format_number(number):
	numbers = ""
	for char in number:
		if char.isdigit() or char == ',':
			numbers += char
	return numbers

def extract_governorprofile(profile):
	data = []
	for coordinate in prof:
		text_profile = extract_image(profile, coordinate)
		text = format_number(text_profile)
		data.append(text)
	return data

def extract_infomation(information):
	data = []
	for coordinate in infor:
		text_profile = extract_image(information, coordinate)
		text = format_number(text_profile)
		data.append(text)
	return data

def extract(governor):
	data = []
	data.extend(extract_governorprofile(governor[0]))
	data.extend(extract_infomation(governor[1]))
	return data

def data_governor(lst):
	data_list = []
	for i in lst:
		data_list.append(extract(i))
	return data_list


def start(emulator, topBXH):

	screnGOVERNOR(emulator, topBXH)
	for i in range(1, topBXH + 1):
		governorprofile = cv2.imread(os.path.join("GovernorProfile", f"governorprofile{i}.bmp"))
		moreinfo = cv2.imread(os.path.join("MoreInfo", f"moreinfo{i}.bmp"))
		governor.append([governorprofile, moreinfo])

	dt = data_governor(governor)
	columns = ["Id", "Name", "T5", "T4", "T3", "T2", "T1", "KillPoint", "Power", "Dead", "Resources"]
	df = pd.DataFrame(dt, columns=columns)

	new_columns = ["Id", "Name", "Power", "Dead", "KillPoint", "T5", "T4", "T3", "T2", "T1", "Resources"]
	df = df.reindex(columns=new_columns)
	df["Name"] = name_data

	df.index += 1
	df.to_excel("Data25891.xlsx", index_label="STT")
	print(df)

emulator = "127.0.0.1:21503"
topBXH = 200
start(emulator, topBXH)