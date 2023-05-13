import discord, os, Adb, architect, duke, scientist, asyncio
from discord.ext import commands
from Adb import ADB

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
ADB_DEVICE = '127.0.0.1:21503'
adb = ADB(ADB_DEVICE)
@bot.command(aliases=["off"])
@commands.has_permissions(administrator=True)
async def turnoff(ctx):
	rp = f"Cảm ơn bạn đã cho tôi thời gian được nghỉ ngơi :sleeping:. Hẹn gặp bạn trong thời gian sớm nhất <3"
	await ctx.send(embed = discord.Embed(title=rp, colour=0xcae1ff))
	await bot.close()

@bot.event
async def on_ready():
	channel = bot.get_channel(...)
	await channel.send(embed=discord.Embed(title="Bot đã sẵn sàng để làm việc!", color=0x00FF1E))
	print("Bot đã sẵn sàng để làm việc!")

bot.is_reset = False
@bot.command()
@commands.has_permissions(administrator=True)
async def resetapp(ctx):
	bot.is_reset = True
	rp = f"Khởi động lại Rise Of Kingdoms! Quá trình khởi động mất 75 năm :grandma::older_man:"
	await ctx.send(embed = discord.Embed(title=rp, colour=0xcae1ff))
	await adb.reset_ROK()
	bot.is_reset = False
	rp2 = discord.Embed(title=f"Khởi động lại hoàn tất. Cảm ơn vì đã đợi <3", colour=0x00FF1E)
	adb.screen_capture('resetapp.png')
	resetapp = discord.File('images/resetapp.png')
	rp2.set_image(url="attachment://resetapp.png")
	await ctx.send(embed=rp2, file=resetapp)

async def title():
	await bot.load_extension("duke")
	await bot.load_extension("scientist")
	await bot.load_extension("architect")

async def main():
	async with bot:
		await title()
		await bot.start(...)

asyncio.run(main())