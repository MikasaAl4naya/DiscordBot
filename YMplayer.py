import asyncio
import os
import parser
from functools import partial
import wget
import discord
from dotenv import load_dotenv
from yandex_music import Client

from utils import Utils

load_dotenv()

YM_Token = os.getenv('Yandex_Token')

YMClient = Client(YM_Token).init()

class YMPlayer(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @staticmethod
    def parse_track(url: str) -> str:
        url_arr = str.split(url, '/')
        url_arr.reverse()

        return str.split(url_arr[0], '?')[0] + ':' + url_arr[2]

    @staticmethod
    def parse_playlist(url: str) -> str:
        url_arr: list[str] = str.split(url, '/')
        url_arr.reverse()

        return YMPlayer.get_user_uid(url_arr[2]) + ':' + str.split(url_arr[0], '?')[0]

    @staticmethod
    def parse_album(url: str) -> str:
        url_arr: list[str] = str.split(url, '/')
        url_arr.reverse()

        return str.split(url_arr[0], '?')[0]

    @staticmethod
    def get_user_uid(user_name: str) -> str:
        return str(YMClient.request.get(YMClient.base_url + '/users/' + user_name)['uid'])

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, track_id: str = None):
        loop = loop or asyncio.get_event_loop()

        if track_id is None:
            track_id: str = cls.parse_track(search)

        return {'webpage_url': track_id, 'requester': ctx.author, 'type': "ym"}

    @classmethod
    async def process_playlist(cls, ctx, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        playlist_id: str = cls.parse_playlist(search)
        to_run = partial(YMClient.playlists_list, playlist_ids=playlist_id)
        data = await loop.run_in_executor(None, to_run)
        # data = YMClient.playlists_list(playlist_ids=playlist_id)
        tracks = data[0].fetch_tracks()
        source = list()
        for track in tracks:
            source.append(await cls.create_source(ctx, None, loop=loop, track_id=track.track.track_id))
        await ctx.send(f'```ini\n[Playlist {data[0].title} added to the Queue.]\n```')
        return source

    @classmethod
    async def process_album(cls, ctx, search: str, *, loop):
        loop = loop or asyncio.get_event_loop()

        album_id = cls.parse_album(search)

        to_run = partial(YMClient.albums_with_tracks, album_id=album_id)
        data = await loop.run_in_executor(None, to_run)

        source = list()
        for disc in data.volumes:
            for track in disc:
                source.append(await cls.create_source(ctx, None, loop=loop, track_id=track.track_id))

        await ctx.send(f'```ini\n[Album {data.title} added to the Queue.]\n```')
        return source

    @classmethod
    async def regather_stream(cls, data, ctx, loop):
        requester = data['requester']

        track_id = data['webpage_url']

        os.makedirs(os.path.abspath(os.curdir) + '\\cache\\' + str(ctx.guild.id), exist_ok=True)
        full_file_name = os.path.abspath(os.curdir) \
                         + '\\cache\\' \
                         + str(ctx.guild.id) \
                         + '\\' \
                         + track_id.replace(':', '_') \
                         + '.mp3'
        full_file_name = full_file_name.replace('\\', '/')
        track_name = ""
        artist = ""
        if not os.path.isfile(full_file_name):
            to_run = partial(YMClient.tracks, track_ids=track_id)
            data = await loop.run_in_executor(None, to_run)
            url: str = data[0].getDownloadInfo()[0].getDirectLink()
            wget.download(url, out=full_file_name)
            track_name = data[0]['title'] + (' ' + data[0]['version'] if data[0]['version'] is not None else '')
            for i in data[0].artists:
                artist += i.name + ','
            artist = artist[:-1]
            Utils.write_metadata(full_file_name, track_name, artist)
        else:
            res = Utils.get_metadata(full_file_name)
            track_name = res['title'][0]
            artist = res['artist'][0]
        title = (artist + ' - ' if len(artist) > 0 else '') + track_name

        await ctx.send(f'```ini\n[Track {title} added to the Queue.]\n```')

        return cls(
            discord.FFmpegPCMAudio(source=full_file_name, options=ffmpegopts,
                                   executable=parser.get('main', 'ffmpeg_path')),
            data={'webpage_url': full_file_name, 'requester': ctx.author, 'title': title},
            requester=requester)
