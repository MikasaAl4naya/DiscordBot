import discord
from config import parser

ffmpegopts: dict[str, str] = {
            'options': '-vn'
        }
class CachePlayer(discord.PCMVolumeTransformer):
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

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop):
        title = search.split(sep='\\\\').pop()

        return {'webpage_url': search, 'requester': ctx.author, 'title': title}

    @classmethod
    async def regather_stream(cls, data):
        requester = data['requester']

        return cls(
            discord.FFmpegPCMAudio(source=data['webpage_url'], options=ffmpegopts,
                                   executable=parser.get('main', 'ffmpeg_path')),
            data=data,
            requester=requester)