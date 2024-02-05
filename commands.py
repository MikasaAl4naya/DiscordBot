import random
import discord

prev_message = None


class Commands():
    def __init__(self, bot):
        self.bot = bot

        @bot.command(aliases=['penis', 'пенис'])
        async def penis_(ctx):
            length = random.randint(1,
                                    10)  # Вероятно, вы хотели использовать random.randint() для генерации случайной длины
            chlen = '8' + '=' * length + 'D'
            mbed = discord.Embed(title=f"Размер пениса", color=discord.Color.from_rgb(255, 255, 255))
            mbed.add_field(name="", value=ctx.author.nick + "'a", inline=False)
            mbed.add_field(name="", value=chlen, inline=False)
            await ctx.reply(embed=mbed)