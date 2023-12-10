from solver_captcha import *
from coordinates_gem import *
from commander import *
from find import *
from count_coordinates import count_gems, count_gems_in_zone_vigo, count_gems_zone_gorlitz
from datetime import datetime
import shutil


def copy_image():
	date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
	source_path = './images/ScreenShot.bmp'
	destination_path = f'./images/RecycleBin/Gem_{date}.bmp'
	shutil.copy(source_path, destination_path)


def status_commander(devices):
	commander_returning = find_returning(devices)
	commander_home = find_home(devices)

	if commander_returning:
		commander = commander_unemployed(commander_returning)
		if not commander:
			return

		click(devices, commander_returning[0], commander_returning[1], 1.5)
		stop_army = find_template(devices, "Stop.bmp")
		if not stop_army:
			status_commander(devices)

		click(devices, stop_army[0], stop_army[1], 0.5)

		address = extract_coordinates_commander(devices)
		return address, commander

	elif commander_home:
		commander = commander_unemployed(commander_home)
		if not commander:
			return

		click(devices, commander_home[0], commander_home[1], 1)
		address = extract_coordinates_commander(devices)

		return address, commander
	
	
def find_commander(devices):
	os.system(f'adb -s {devices} shell input touchscreen swipe 1225 200 1225 410 200')
	time.sleep(1)
	status_result = status_commander(devices)
	if status_result:
		return status_result

	os.system(f'adb -s {devices} shell input touchscreen swipe 1225 410 1225 200 200')
	time.sleep(1)
	status_result = status_commander(devices)
	if status_result:
		return status_result
	

def farm_gem(devices, rok, index, coordinate_city_hall):
	check_confirm(devices, rok)
	solver_captcha(devices, rok)
	check_out_city(devices)
	check_status(devices, rok)

	turn = 0

	while True:
		if turn > 10:
			farm_gem(devices, rok, index, coordinate_city_hall)

		status_armies = all_armies_busy(devices)
		if status_armies:
			commander = find_commander(devices)
			while True:
				if not commander:
					break

				print(f"Gem: {count_gems()} - Gorlitz {count_gems_zone_gorlitz()}/{gorlitz} - Vigo {count_gems_in_zone_vigo()}/{vigo}")
				nearest_gem_mine = find_nearest_gem_mine_2589(commander[0][0], commander[0][1])
				if not nearest_gem_mine:
					break

				search_coordinate(devices, rok, index, nearest_gem_mine[0], nearest_gem_mine[1])
				if not check_gem_point(devices):
					continue
				copy_image()

				gather_commander(devices, commander[1])
				solver_captcha(devices, rok)

				commander = find_commander(devices)
				if not commander:
					break

		else:
			while True:
				print(f"Gem: {count_gems()} - Gorlitz {count_gems_zone_gorlitz()}/{gorlitz} - Vigo {count_gems_in_zone_vigo()}/{vigo}")
				nearest_gem_mine = find_nearest_gem_mine_2589(coordinate_city_hall[0], coordinate_city_hall[1])
				if not nearest_gem_mine:
					break

				search_coordinate(devices, rok, index, nearest_gem_mine[0], nearest_gem_mine[1])
				if not check_gem_point(devices):
					continue
				copy_image()

				gather(devices)
				solver_captcha(devices, rok)
				if all_armies_busy(devices):
					break

		turn += 1
		time_sleep = random.randint(30, 45)
		print(f"Sleep {time_sleep}s!")
		time.sleep(time_sleep)
		check_confirm(devices, rok)


def start_bot():
	devices = "emulator-5554"
	rok = "com.rok.gp.vn"
	index = 0
	coordinate_city_hall = (565, 564)

	try:
		farm_gem(devices, rok, index, coordinate_city_hall)
	except Exception as e:

		date = datetime.now().strftime("%H_%M_%S_%d_%m_%Y")
		source_path = './images/ScreenShot.bmp'
		destination_path = f'./images/RecycleBin/Image_{date}.bmp'
		shutil.copy(source_path, destination_path)

		handle_error(devices, e, rok)

	# gather(devices)
	# gather_commander(devices, "Sarka")
	# check_Gem_Point(devices)
	# find_nearest_gem_mine(856, 248)
	# AllArmiesBusy(devices)
	# start_time = datetime.now()
	# search_coordinate(devices, rok, index, 589, 600)
	# end_time = datetime.now()
	#
	# running_time = (end_time - start_time).total_seconds()
	# print("Thời gian thực hiện -", running_time)
	

def handle_error(devices, error, rok):
	print(f"Error: {error}")

	end_application(devices, rok)
	start_application(devices, rok)
	start_bot()


gorlitz = 30
vigo = 30
if __name__ == "__main__":
	start_bot()
