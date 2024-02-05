import asyncio

import discord
import requests
from bs4 import BeautifulSoup
from discord import FFmpegPCMAudio
from discord.ext import commands
from yandex import YandexMusic as music

global queue
class YandexPlay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = []  # Объявляем queue как атрибут класса
    @commands.command()
    async def stopy(self,ctx):
        await ctx.voice_client.disconnect()

    # накодил zacky
    @commands.command()
    async def pausey(self,ctx):
        server = ctx.message.guild
        voice_channel = ctx.voice_client  # изменил, если обратно вернуть то вместо ctx поставить server
        if voice_channel.is_playing():
            voice_channel.pause()
            await ctx.send('**Поставили на паузу**')
        else:
            if voice_channel.is_paused() == True:
                await ctx.send('**Уже поставлено на паузу**')
            else:
                await ctx.send('**Упс...похоже, нет проигрываемой музыки**')

    @commands.command()
    async def resumey(self,ctx):
        server = ctx.message.guild
        voice_channel = ctx.voice_client  # изменил, если обратно вернуть то вместо ctx поставить server
        if ctx.voice_client.is_paused() == True:
            voice_channel.resume()
            await ctx.send('**Возобновили**')
        else:
            await ctx.send('**Вы и не ставили на паузу**')

    @commands.command()
    async def nexty(self,ctx):
        if len(self.queue) > 0:
            voice_channel = ctx.voice_client
            voice_channel.stop()
            self.queue.pop(0)
            info = music.infoTrack(self.queue[0])
            url = self.queue[0]
            durationTrack = info.get('duration')
            await self.playLocalFile(ctx, int(float(durationTrack)), url)
        else:
            await ctx.send('**Нет треков в очереди**')
            pass

    @commands.command()
    async def cleany(self,ctx):
        if len(self.queue) == 1:
            await ctx.send('**Нет треков в очереди, очищать нечего**')
        else:
            for tracks in reversed(range(1, len(self.queue))):
                self.queue.pop(tracks)
            await ctx.send('**Очередь очищена, добавляй следующие треки**')

    @commands.command()
    async def addy(self,ctx):
        added_track_url = ctx.message.content[4:].format(ctx.message)
        self.queue.append(added_track_url)
        await ctx.send(self.queue)
        await ctx.send('**Добавлен новый трек в очередь**')

    async def secondToMinutes(self,second):
        second = int(float(second))
        h = str(second // 3600)
        m = (second // 60) % 60
        s = second % 60
        if m < 10:
            m = '0' + str(m)
        else:
            m = str(m)
        if s < 10:
            s = '0' + str(s)
        else:
            s = str(s)
        return h + ':' + m + ':' + s
    @commands.command()
    async def play_yandex(self, ctx: commands.Context):

        url = ctx.message.content[6:].format(ctx.message)
        checkInTrack = url.split("/")
        if checkInTrack[-2] == "track":
            if ctx.message.content.startswith('#play'):
                info = music.infoTrack(url)
                durationTrack = info.get('duration')
                await self.playLocalFile(ctx, int(float(durationTrack)), url)
        else:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            quotes = soup.find_all('a', class_='d-track__title deco-link deco-link_stronger')
            self.queue = []
            print(type(self.queue))
            for title in quotes:
                s = title.text.strip(), title.get('href')
                url = "https://music.yandex.ru" + s[1]
                info = music.infoTrack(url)
                queue.append(url)
                durationTrack = info.get('duration')
                await self.playLocalFile(ctx, int(float(durationTrack)), url)

    @commands.command()
    async def playLocalFile(self, ctx, second, url):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("Вы не подключены к голосовому чату :(")
            return
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        url_parts = url.split('/')
        trackID = url_parts[-1]
        url = music.extractDirectLinkToTrack(trackID)
        source = FFmpegPCMAudio(url)
        player = voice.play(source)

        await asyncio.sleep(second)

async def setup(bot):
    await bot.add_cog(YandexPlay(bot))