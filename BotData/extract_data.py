import cv2
import os
import pytesseract
import datetime
import pandas as pd


pid = (475, 150, 695, 185)
t1 = (1000, 335, 1145, 370)
t2 = (1000, 370, 1145, 405)
t3 = (1000, 405, 1145, 440)
t4 = (1000, 440, 1145, 475)
t5 = (1000, 475, 1145, 510)
killpoint = (964, 95, 1140, 155)
power = (650, 95, 815, 155)
dead = (900, 340, 1085, 405)
resource = (890, 520, 1085, 590)


infor = [killpoint, power, dead]
prof = [pid, t5, t4, t3, t2, t1]
governor = []
name_data = []


def format_number(number):
	numbers = ""
	for char in number:
		if char.isdigit():
			numbers += char
	return numbers


def count_unique_numbers(data_extract):
	unique_numbers = set(data_extract)
	return len(unique_numbers)


def run_extract_image(ext_image, coordinate):
	data_extract = []
	thre = [153, 155, 159, 160, 162, 168, 172]
	for i in thre:
		threshold = cv2.threshold(ext_image, i, 255, cv2.THRESH_BINARY_INV)[1]
		myconfig = r"--oem 3 --psm 11"
		language = "digits_comma+eng"

		try:
			if coordinate in (pid,):
				text = pytesseract.image_to_string(threshold, config=myconfig)
			else:
				text = pytesseract.image_to_string(threshold, lang=f"{language}", config=myconfig)
			text = format_number(text.strip())
			text = int(text)
		except:
			text = 0

		# cv2.imshow("img", threshold)
		# cv2.waitKey(0)
		# print(f"{i}:{text}")
		data_extract.append(text)
	return data_extract


def extract_image(image, coordinate):
	x, y, w, h = coordinate
	ext_image = image[y:h, x:w, 1]

	data_extract = run_extract_image(ext_image, coordinate)
	common_number = max(set(data_extract), key=data_extract.count)

	# print(data_extract)
	# print(count_unique_numbers(data_extract))
	# print(common_number)
	# cv2.imshow("img", ext_image)
	# cv2.waitKey(0)
	return common_number


def extract_governorprofile(profile):
	data = []
	for coordinate in prof:
		text = extract_image(profile, coordinate)
		if text != 0:
			if coordinate == t5:
				text /= 20
			elif coordinate == t4:
				text /= 10
			elif coordinate == t3:
				text /= 4
			elif coordinate == t2:
				text /= 2
			elif coordinate == t1:
				text *= 5
			text = int(text)
		data.append(text)
	return data


def extract_infomation(information):
	data = []
	for coordinate in infor:
		text_profile = extract_image(information, coordinate)
		data.append(text_profile)
	return data


def extract(governor):
	data = []
	data.extend(extract_governorprofile(governor[0]))
	data.extend(extract_infomation(governor[1]))
	return data


def data_governor(lst):
	data_list = []
	top = 0
	for i in lst:
		data_list.append(extract(i))
		top += 1
		print(f"Hoàn thành trích xuất dữ liệu top {top}")
	return data_list


def add_data_name(file_data, txt_name):
	path = f"D:/Code Python/BotData/Data/{file_data}/{txt_name}.txt"
	with open(path, "r", encoding="utf-8") as file:
		for line in file:
			name = line.strip()
			name_data.append(name)
	return name_data


def start(file_data, file_xlsx, txt_name):
	start_time = datetime.datetime.now()
	start_time = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
	print("Bắt đầu quét dữ liệu - ", start_time)

	top = add_data_name(file_data, txt_name)
	top = len(top)

	for i in range(1, top+1):
		governorprofile = cv2.imread(os.path.join(f"Data/{file_data}/GovernorProfile", f"governorprofile{i}.bmp"))
		moreinfo = cv2.imread(os.path.join(f"Data/{file_data}/MoreInfo", f"moreinfo{i}.bmp"))
		governor.append([governorprofile, moreinfo])

	dt = data_governor(governor)
	columns = ["Id", "T5", "T4", "T3", "T2", "T1", "KillPoint", "Power", "Dead"]
	df = pd.DataFrame(dt, columns=columns)
	df.insert(1, "Name", "")

	new_columns = ["Id", "Name", "Power", "Dead", "KillPoint", "T5", "T4", "T3", "T2", "T1"]
	df = df.reindex(columns=new_columns)
	df["Name"] = name_data

	df.index += 1
	df.to_excel(f"CalculatingData/{file_xlsx}.xlsx", index_label="Rank")

	end_time = datetime.datetime.now()
	end_time = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
	print("Quét dữ liệu hoàn tất - ", end_time)

	running_time = end_time - start_time
	running_time = datetime.timedelta(seconds=running_time.seconds)
	print("Thời gian thực hiện - ", running_time)


print("File data: ")
file_data = input()

txt_name = file_data+"_Name"

print("Tên file xlsx: ")
xlsx_name = input()

start(file_data, xlsx_name, txt_name)
