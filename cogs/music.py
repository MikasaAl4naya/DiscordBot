import asyncio
import random
from datetime import datetime

import discord
import typing
import wavelink
from discord.ext import commands
from typing import cast
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())
        # Создайте словарь для хранения очередей для каждого сервера
        self.queues = {}

    async def create_nodes(self):
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot, host="localhost", port=2333, password="youshallnotpass", region="russia")

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"Node <{node.identifier}> is now Ready!")

    @commands.command(name="join", aliases=["connect", "summon"])
    async def join_command(self, ctx: commands.Context, channel: typing.Optional[discord.VoiceChannel]):
        if channel is None:
            channel = ctx.author.voice.channel

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is not None:
            if player.is_connected():
                return await ctx.send("Бот уже на канале")

        await channel.connect(cls=wavelink.Player)
        mbed = discord.Embed(title=f"Connected to {channel.name}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(name="leave", alises=["disconnect"])
    async def leave_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.reply("В канал зайди")

        await player.disconnect()
        mbed = discord.Embed(title="Disconnected", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(aliases=['Play', 'PLAY', 'играй', 'ИГРАЙ', 'Играй', 'сыграй',
                          'Сыграй', 'СЫГРАЙ', 'здфн', 'Здфн', 'ЗДФН', 'p', 'P',
                          'pl', 'PL', 'Pl', 'з', 'З', 'зд', 'ЗД', 'Зд', 'Плей',
                          'ПЛЕЙ', 'плей'])
    async def play(self, ctx: commands.Context, *, search: str):
        search = await wavelink.YouTubeTrack.search(query=search, return_first=True)
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        # Проверьте, существует ли очередь для сервера
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = asyncio.Queue()
        # Поместите трек в очередь
        await self.queues[ctx.guild.id].put(search)
        # Если плеер не играет, начните воспроизведение
        if not vc.is_playing():
            await self.play_queue(ctx, vc)

    async def play_queue(self, ctx, vc):
        # Получите очередь для сервера
        queue = self.queues[ctx.guild.id]
        # Пока в очереди есть треки, воспроизводим их
        while not queue.empty():
            # Извлеките трек из очереди
            track = await queue.get()
            # Поместите трек обратно в очередь (перед воспроизведением)
            queue.put_nowait(track)
            # Воспроизведите трек
            await vc.play(track)
            # Дождитесь окончания воспроизведения
            while vc.is_playing():
                await asyncio.sleep(1)
            # Трек воспроизведен, теперь можно удалить его из очереди
            await queue.get()
        # Если все треки воспроизведены, отключите бота от голосового канала
        await vc.disconnect()

    @commands.command(aliases=['Queue', 'QUEUE', 'йгугу', 'Йгугу', 'ЙГУГУ', 'очередь',
                          'Очередь', 'ОЧЕРЕДЬ', 'список', 'Список', 'СПИСОК',
                          'list', 'List', 'LIST', 'дшые', 'Дшые', 'ДШЫЕ', 'Лист',
                          'лист', 'ЛИСТ', 'песни', 'Песни', 'ПЕСНИ', 'songs',
                          'Songs', 'SONGS', 'ыщтпы', 'ЫЩТПЫ', 'Ыщтпы', 'q'])
    async def queue(self, ctx: commands.Context):
        """Show the current queue."""
        # Получите очередь для сервера
        queue = self.queues.get(ctx.guild.id)
        if not queue or queue.empty():
            return await ctx.send("Очередь пуста.")

        # Получите текущий трек без его удаления из очереди
        current_track = await queue.get()

        # Соберите треки из очереди
        tracks = [
            f"{index + 1}. {track.title} - {str(int(track.duration // 60))}:{str(int(track.duration) % 60).zfill(2)}"
            for index, track in enumerate(queue._queue)
        ]

        # Отправьте сообщение с текущей очередью в виде Embed
        embed = discord.Embed(title="Текущая очередь",
                              color=discord.Color.from_rgb(52, 152, 219))  # Используйте цвет по вашему выбору

        # Добавьте текущий трек крупным шрифтом с эмодзи
        embed.add_field(name="🎶 Сейчас играет",
                        value=f"**{current_track.title}** - *{str(int(current_track.duration // 60))}:{str(int(current_track.duration) % 60).zfill(2)}*",
                        inline=False)

        # Добавьте список остальных треков
        embed.add_field(name="📜 Очередь", value="\n".join(tracks), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="stop")
    async def stop_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.reply("В канал зайди")

        if player.is_playing:
            await player.stop()
            mbed = discord.Embed(title="Стопанул", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Ниче не играет сейчас")

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

    @commands.command(name="volume")
    async def volume_command(self, ctx: commands.Context, to: int):
        if to > 100:
            return await ctx.send("Громкость должен быть от 0 до 100")
        elif to < 1:
            return await ctx.send("Громкость должен быть от 0 до 100")

        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        await player.set_volume(to)
        mbed = discord.Embed(title=f"Теперь громкость {to}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)

    @commands.command(aliases=['sk', 'next', 'следующая', 'скип', 'скипнуть'])
    async def skip(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.reply("В канал зайди")

        if player.is_playing:
            await player.stop()
            mbed = discord.Embed(title="Пропустил текущий трек", color=discord.Color.from_rgb(255, 255, 255))
            await ctx.send(embed=mbed)
        else:
            return await ctx.send("Ниче не играет сейчас")

    @commands.command(name="shuffle")
    async def shuffle_command(self, ctx: commands.Context):
        """Shuffle the music queue."""
        # Получите очередь для сервера
        queue = self.queues.get(ctx.guild.id)
        if not queue or queue.empty():
            return await ctx.send("Очередь пуста.")

        # Поместите треки в список для перемешивания
        tracks_to_shuffle = list(queue._queue)
        random.shuffle(tracks_to_shuffle)

        # Очистите текущую очередь и добавьте перемешанные треки
        queue._queue.clear()
        for track in tracks_to_shuffle:
            await queue.put(track)

        await ctx.send("Очередь была перемешана.")

async def setup(client):
  await client.add_cog(Music(client))