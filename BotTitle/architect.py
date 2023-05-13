import time
import discord, os, Adb, sqlite3
from discord.ext import commands
from Adb import ADB
import asyncio

conn = sqlite3.connect('coordinates.db')
cursor = conn.cursor()
ADB_DEVICE = '127.0.0.1:21503'
adb = ADB(ADB_DEVICE)

class Architect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.architect_holder = None
        self.bot.architect_list = []
        self.bot.is_reset = False

    @commands.command(aliases=["arch", "Arch", "Architect"])
    async def architect(self, ctx, server=None, x_coordinate=None, y_coordinate=None):
        await self.architect_worker(ctx, server, x_coordinate, y_coordinate)
        await self.pop_architect()

    async def pop_architect(self):
        await asyncio.sleep(60)
        self.bot.architect_holder = None
        if len(self.bot.architect_list) > 0:
            event = self.bot.architect_list.pop(0)
            event.set()

    async def architect_worker(self, ctx, server, x_coordinate, y_coordinate):
        user_name = ctx.author.name
        position_list = len(self.bot.architect_list)

        if self.bot.is_reset:
            await ctx.send(
                embed=discord.Embed(title=f"Bot đang được khởi động lại, vui lòng thử lại sau.", colour=0xcae1ff))
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

            if self.bot.architect_holder is not None:
                rp2 = f":index_pointing_at_the_viewer:'{user_name}' '{server}' '{x_coordinate}' '{y_coordinate} được cấp architect, vị trí của bạn là {position_list + 2}!"
                await ctx.send(embed=discord.Embed(title=rp2, colour=0x00F3FF))
                event = asyncio.Event()
                self.bot.architect_list.append(event)
                await event.wait()

            self.bot.architect_holder = ctx.author
            responses1 = f"Cấp tước vị architect cho '{user_name}' '{server}' '{x_coordinate}' '{y_coordinate}'"
            await ctx.send(embed=discord.Embed(title=responses1, colour=0x00F3FF))


            adb.screen_capture('screenshot.bmp')
            adb.search_coordinate(server, x_coordinate, y_coordinate)
            adb.click_home()
            adb.title_architect()

            rp = discord.Embed(title=f"'{user_name}' được cấp tước thành công. Bạn có {60} giây giữ tước!",
                               colour=0x00F3FF)
            await asyncio.sleep(1)
            adb.screen_capture('done_architect.png')
            done_architect = discord.File('images/done_architect.png')
            rp.set_image(url="attachment://done_architect.png")
            await ctx.send(embed=rp, file=done_architect)
            adb.click(640, 360)

async def setup(bot):
    await bot.add_cog(Architect(bot))