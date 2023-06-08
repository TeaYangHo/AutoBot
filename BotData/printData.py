import sqlite3
import pandas as pd

def formatNumber(number):
	number = float(number)
	formatted_number = "{:,.0f}".format(number).replace(",", ".")
	return formatted_number

def governor(ID):
	data = pd.read_excel('Data2589.xlsx')
	conn = sqlite3.connect('Data2589.db')
	data.to_sql('Governor', conn, if_exists='replace', index=False)
	cursor = conn.cursor()
	query = f"SELECT * FROM Governor WHERE Id = {ID}"
	cursor.execute(query)
	player_info = cursor.fetchone()

	if player_info:
		print("Thông tin người chơi:")
		print("Id:", player_info[0])
		print("Name:", player_info[1])
		print("T1:", formatNumber(player_info[2]))
		print("T2:", formatNumber(player_info[3]))
		print("T3:", formatNumber(player_info[4]))
		print("T4:", formatNumber(player_info[5]))
		print("T5:", formatNumber(player_info[6]))
		print("KillPoint:", formatNumber(player_info[7]))
		print("Power:", formatNumber(player_info[8]))
		print("Dead:", formatNumber(player_info[9]))
		print("Resources:", formatNumber(player_info[10]))
	else:
		print("Không tìm thấy thông tin người chơi.")
	conn.close()

print("Nhập ID thống đốc: ")
ID = input()
governor(ID)
115559251
