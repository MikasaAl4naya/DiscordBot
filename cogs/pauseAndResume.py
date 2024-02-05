import discord
import wavelink
from discord.ext import commands


class PauseResume(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""
    @commands.command(name="pause")
    async def pause_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        if player is None:
            return await ctx.reply("В канал зайди")
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                mbed = discord.Embed(title="На паузе", color=discord.Color.from_rgb(255, 255, 255))
                return await ctx.send(embed=mbed)
            else:
                return await ctx.send("Сейчас ничего не играет")
        else:
            return await ctx.send("Уже на паузе дада я")

    @commands.command(name="resume")
    async def resume_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)
        if player is None:
            return await ctx.send("Бот не подключен ни к одному каналу")
        if player.is_paused():
            await player.resume()
            mbed = discord.Embed(title="Продолжил", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Плеер не на паузе")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PauseResume(bot))