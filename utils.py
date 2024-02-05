import mutagen
from mutagen.easyid3 import EasyID3


class Utils:
    # 1 - трек яндекс музыки
    # 2 - видео с ютуба
    # 3 - плейлист яндекс музыки
    # 4 - альбом яндекс музыки
    @staticmethod
    def parse_url(url: str):
        if 'yandex' in url:
            if 'users' in url and 'playlists' in url:
                return 3
            elif 'album' in url and 'track' not in url:
                return 4
            else:
                return 1
        if 'youtu' in url:
            return 2
        return -1

    @staticmethod
    def write_metadata(full_file_path: str, track_name: str, artist: str):
        try:
            audiofile = EasyID3(full_file_path)
        except mutagen.id3.ID3NoHeaderError:
            audiofile = mutagen.File(full_file_path, easy=True)
            audiofile.add_tags()
        audiofile['artist'] = artist
        audiofile['title'] = track_name

        audiofile.save();

    @staticmethod
    def get_metadata(full_file_path: str):
        audiofile = EasyID3(full_file_path)
        return {'artist': audiofile['artist'], 'title': audiofile['title']}
