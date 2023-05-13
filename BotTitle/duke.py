import time

import discord, os, Adb, sqlite3
from discord.ext import commands
from Adb import ADB
import asyncio

conn = sqlite3.connect('coordinates.db')
cursor = conn.cursor()
ADB_DEVICE = '127.0.0.1:21503'
adb = ADB(ADB_DEVICE)

class Duke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.duke_setup = True
        self.bot.duke_holder = None
        self.bot.duke_list = []
        self.bot.duke_time = None
        self.bot.is_reset = False

    @commands.command(aliases=["dukeoff"])
    @commands.has_permissions(administrator=True)
    async def offduke(self, ctx):
        self.bot.duke_setup = False
        await ctx.send(embed=discord.Embed(title=f"Duke đã được dừng!", colour=0xFF9C30))

    @commands.command(aliases=["dukeon"])
    @commands.has_permissions(administrator=True)
    async def onduke(self, ctx):
        self.bot.duke_setup = True
        await ctx.send(embed=discord.Embed(title=f"Duke đã được bật!", colour=0xFF9C30))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setduketime(self, ctx, time: int):
        self.bot.duke_time = time
        rp_sdt = f"Thời gian sử dụng được thiết lập. Bạn được giữ duke trong {self.bot.duke_time} seconds."

        await ctx.send(embed=discord.Embed(title=rp_sdt, colour=0xFF9C30))

    async def pop_duke(self):
        if self.bot.duke_time == None:
            await asyncio.sleep(120)
        else:
            await asyncio.sleep(self.bot.duke_time)
        self.bot.duke_holder = None
        if len(self.bot.duke_list) > 0:
            event = self.bot.duke_list.pop(0)
            event.set()

    async def duke_worker(self, ctx, server, x_coordinate, y_coordinate):
        user_name = ctx.author.name
        position_list = len(self.bot.duke_list)

        if self.bot.is_reset:
            await ctx.send(
                embed=discord.Embed(title=f"Bot đang được khởi động lại, vui lòng thử lại sau.", colour=0xcae1ff))
        else:
            if not self.bot.duke_setup:
                await ctx.send(embed=discord.Embed(title=f"Duke đang dừng hoạt động!", colour=0xFF9C30))
            else:
                if server and x_coordinate and y_coordinate:
                    try:
                        cursor.execute("INSERT INTO coordinates VALUES (?, ?, ?, ?)",
                                       (user_name, server, x_coordinate, y_coordinate))
                    except sqlite3.IntegrityError:
                        cursor.execute("UPDATE coordinates SET server = ?, x = ?, y = ? WHERE user_name = ?",
                                       (server, x_coordinate, y_coordinate, user_name))

                    conn.commit()
                else:
                    cursor.execute("SELECT * FROM coordinates WHERE user_name = ?", (user_name,))
                    row = cursor.fetchone()
                    if row:
                        server, x_coordinate, y_coordinate = row[1], row[2], row[3]
                    else:
                        await ctx.send(embed=discord.Embed(
                            title=f"{user_name} tọa độ của bạn chưa được lưu, vui lòng cung cấp tọa độ của bạn!",
                            colour=0xFFFFFF))
                        return

                if self.bot.duke_holder is not None:
                    rp2 = f":index_pointing_at_the_viewer:'{user_name}' '{server}' '{x_coordinate}' '{y_coordinate} được cấp duke, vị trí của bạn là {position_list + 2}!"
                    await ctx.send(embed=discord.Embed(title=rp2, colour=0xFF9C30))
                    event = asyncio.Event()
                    self.bot.duke_list.append(event)
                    await event.wait()

                self.bot.duke_holder = ctx.author
                responses1 = f"Cấp tước vị duke cho '{user_name}' '{server}' '{x_coordinate}' '{y_coordinate}'"
                await ctx.send(embed=discord.Embed(title=responses1, colour=0xFF9C30))

                adb.screen_capture('screenshot.bmp')
                adb.search_coordinate(server, x_coordinate, y_coordinate)
                adb.click_home()
                adb.title_duke()

                await asyncio.sleep(1)
                adb.screen_capture('done_duke.png')
                done_duke = discord.File('images/done_duke.png')

                if self.bot.duke_time == None:
                    rp = discord.Embed(title=f"'{user_name}' được cấp tước thành công. Bạn có {120} giây giữ tước!",
                                       colour=0xFF9C30)
                    rp.set_image(url="attachment://done_duke.png")
                    await ctx.send(embed=rp, file=done_duke)
                else:
                    rp_sdt = discord.Embed(
                        title=f"'{user_name}' được cấp tước thành công. Bạn có {self.bot.duke_time} giây giữ tước!",
                        colour=0xFF9C30)
                    rp_sdt.set_image(url="attachment://done_duke.png")
                    await ctx.send(embed=rp_sdt, file=done_duke)
                adb.click(640, 360)


    @commands.command(aliases=["Duke", "DUKE"])
    async def duke(self, ctx, server=None, x_coordinate=None, y_coordinate=None):
        await self.duke_worker(ctx, server, x_coordinate, y_coordinate)
        await self.pop_duke()

async def setup(bot):
    await bot.add_cog(Duke(bot))