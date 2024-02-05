import asyncio
import re

import discord
import wavelink
from discord.ext import commands
from wavelink.ext import spotify


class Play(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.youtube_playlist_regex = re.compile(
            r"(https://)(www\.)?(youtube\.com)\/(?:watch\?v=|playlist)?(?:.*)?&?(list=.*)"
        )
        self.youtube_track_regex = re.compile(
            r"^https?://(?:www\.)?youtube\.com/watch\?v=[a-zA-Z0-9_-]{11}$"
        )
        self.youtubemusic_track_regex = re.compile(
            r"(?:https?:\/\/)?(?:www\.)?(?:music\.)?youtube\.com\/(?:watch\?v=|playlist\?list=)[\w-]+"
        )
        self.queues = {}
        self.current_queue_messages = {}

    @commands.command(aliases=['Play', 'PLAY', 'играй', 'ИГРАЙ', 'Играй', 'сыграй',
                               'Сыграй', 'СЫГРАЙ', 'здфн', 'Здфн', 'ЗДФН', 'p', 'P',
                               'pl', 'PL', 'Pl', 'з', 'З', 'зд', 'ЗД', 'Зд', 'Плей',
                               'ПЛЕЙ', 'плей'])
    async def play(self, ctx: commands.Context, *, search: str):
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        print(type(vc))
        # Проверьте, существует ли очередь для сервера
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = asyncio.Queue()
        # Получите треки для запроса
        tracks = await wavelink.YouTubeTrack.search(query=search)
        # Если возвращен плейлист, добавьте все его треки в очередь
        if isinstance(tracks, wavelink.YouTubePlaylist):
            for track in tracks.tracks:
                await self.queues[ctx.guild.id].put(track)
        elif isinstance(tracks, list):
            await self.queues[ctx.guild.id].put(tracks[0])
        # Если плеер не играет, начните воспроизведение
        if not vc.is_playing():
            queue = self.queues[ctx.guild.id]
            # Пока в очереди есть треки, воспроизводим их
            while not queue.empty():
                # Извлеките трек из очереди
                track = queue._queue[0]
                # Воспроизведите трек
                await vc.play(track)
                print(type(track))
                # Удаляем предыдущее сообщение с очередью, если оно существует
                if ctx.guild.id in self.current_queue_messages:
                    await self.current_queue_messages[ctx.guild.id].delete()
                # Показать текущую очередь
                await self.queue(ctx)
                # Дождитесь окончания воспроизведения
                while vc.is_playing():
                    await asyncio.sleep(1)
                # Удалите воспроизведенный трек из очереди
                if track in queue._queue:
                    try:
                        queue._queue.popleft()
                    except IndexError:
                        pass
                        print("Список пуст")


    async def play_queue(self, ctx, vc):
        # Получите очередь для сервера
        queue = self.queues[ctx.guild.id]
        # Пока в очереди есть треки, воспроизводим их
        while not queue.empty():
            # Извлеките трек из очереди
            track = queue._queue[0]
            # Воспроизведите трек
            await vc.play(track)
            # Удаляем предыдущее сообщение с очередью, если оно существует
            if ctx.guild.id in self.current_queue_messages:
                await self.current_queue_messages[ctx.guild.id].delete()
            # Показать текущую очередь
            await self.queue(ctx)
            # Дождитесь окончания воспроизведения
            while vc.is_playing():
                await asyncio.sleep(1)
            # Удалите воспроизведенный трек из очереди
            queue._queue.popleft()
        # Если все треки воспроизведены, отключите бота от голосового канала
        (await vc.disconnect()

         @ commands.command(aliases=['Queue', 'QUEUE', 'йгугу', 'Йгугу', 'ЙГУГУ', 'очередь',
                                     'Очередь', 'ОЧЕРЕДЬ', 'список', 'Список', 'СПИСОК',
                                     'list', 'List', 'LIST', 'дшые', 'Дшые', 'ДШЫЕ', 'Лист',
                                     'лист', 'ЛИСТ', 'песни', 'Песни', 'ПЕСНИ', 'songs',
                                     'Songs', 'SONGS', 'ыщтпы', 'ЫЩТПЫ', 'Ыщтпы', 'q']))

    async def queue(self, ctx: commands.Context):
        """Show the current queue."""
        # Получите очередь для сервера
        queue = self.queues.get(ctx.guild.id)
        if not queue or queue.empty():
            return await ctx.send("Очередь пуста.")
        # Получите текущий трек без его удаления из очереди
        current_track = await queue.get()
        queue.put_nowait(current_track)
        # Получите следующие 5 треков из очереди
        next_tracks = [
            track for _, track in zip(range(5), iter(queue._queue))
        ]
        # Соберите треки из очереди
        tracks = [
            f"{index + 1}. {track.title} - {str(int(track.duration // 60))}:{str(int(track.duration) % 60).zfill(2)}"
            for index, track in enumerate(next_tracks)
        ]
        # Если в очереди только один трек, не создавайте список
        if len(tracks) > 1:
            # Отправьте сообщение с текущей очередью в виде Embed
            embed = discord.Embed(title="Текущая очередь",
                                  color=discord.Color.from_rgb(52, 152, 219))  # Используйте цвет по вашему выбору
            # Добавьте текущий трек крупным шрифтом с эмодзи
            embed.add_field(name="🎶 Сейчас играет",
                            value=f"**{current_track.title}** - *{str(int(current_track.duration // 60))}:{str(int(current_track.duration) % 60).zfill(2)}*",
                            inline=False)
            # Добавьте список следующих треков
            embed.add_field(name="📜 Очередь", value="\n".join(tracks), inline=False)
            # Проверим, есть ли предыдущее сообщение и удалим его
            if ctx.guild.id in self.current_queue_messages:
                try:
                    await self.current_queue_messages[ctx.guild.id].delete()
                except discord.NotFound:
                    pass  # Если сообщение уже удалено
            # Отправьте сообщение с текущей очередью и сохраните его для последующего удаления
            self.current_queue_messages[ctx.guild.id] = await ctx.send(embed=embed)
        else:
            # Если в очереди всего один трек, отправьте сообщение только о текущем треке
            embed = discord.Embed(title="Сейчас играет",
                                  color=discord.Color.from_rgb(52, 152, 219))  # Используйте цвет по вашему выбору

            # Добавьте текущий трек крупным шрифтом с эмодзи
            embed.add_field(name="🎶 Сейчас играет",
                            value=f"**{current_track.title}** - *{str(int(current_track.duration // 60))}:{str(int(current_track.duration) % 60).zfill(2)}*",
                            inline=False)


    @commands.command(name="stop")
    async def stop_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.reply("В канал зайди")

        if player.is_playing:
            # Остановите воспроизведение текущего трека
            await player.stop()

            # Очистите очередь
            queue = self.queues.get(ctx.guild.id)
            if queue:
                queue._queue.clear()

            # Отправьте сообщение об остановке
            mbed = discord.Embed(title="Стопанул", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Ниче не играет сейчас")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Play(bot))
