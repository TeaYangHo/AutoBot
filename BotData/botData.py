import discord
from discord.ext import commands
import sqlite3
import pandas as pd

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)


def format_number(number):
	formatted_number = "{:,.0f}".format(number)
	return formatted_number


def get_player_info(ID):
	data = pd.read_excel('DKP2589.xlsx')
	conn = sqlite3.connect('DKP2589.db')
	data.to_sql('Governor', conn, if_exists='replace', index=False)
	cursor = conn.cursor()
	query = f"SELECT * FROM Governor WHERE Id = {ID}"
	cursor.execute(query)
	player_info = cursor.fetchone()
	conn.close()
	return player_info


@bot.event
async def on_ready():
	channel = bot.get_channel(1122440769211469925)
	await channel.send('Bot đã sẵn sàng để làm việc!')


@bot.command(aliases=["dkp", "Dkp", "DKP"])
async def start_bot(ctx, ID):
	player_info = get_player_info(ID)
	user_name = ctx.author.name
	if player_info:
		embed = discord.Embed(title=f"Xếp hạng người chơi {user_name}: {int(player_info[0])}", colour=0x01efe3)
		embed.add_field(name="Id", value=int(player_info[1]))
		embed.add_field(name="Name", value=player_info[2])
		embed.add_field(name="Power", value=format_number(player_info[3]))
		embed.add_field(name="", value="\n", inline=False)
		embed.add_field(name="Power Variation", value=format_number(player_info[4]))
		embed.add_field(name="Dead", value=format_number(player_info[5]))
		embed.add_field(name="", value="\n", inline=False)
		embed.add_field(name="Kill Point", value=format_number(player_info[6]))
		embed.add_field(name="T5", value=format_number(player_info[7]))
		embed.add_field(name="T4", value=format_number(player_info[8]))
		embed.add_field(name="T3", value=format_number(player_info[9]))
		embed.add_field(name="T2", value=format_number(player_info[10]))
		embed.add_field(name="T1", value=format_number(player_info[11]))
		embed.add_field(name="Resources", value=format_number(player_info[12]))
		await ctx.send(embed=embed)
	else:
		responses = f"Không tìm thấy ID người chơi {user_name}. Vui lòng kiểm tra lại"
		await ctx.send(embed=discord.Embed(title=responses, colour=0xef0101))


bot.run('MTEyMzU0MTI1NTY4MzU5MjE5Mg.GhqeRB.qJGlX5AB3CUQQHBvm7Pkv0H6iU__yhO4_4MwBc')
