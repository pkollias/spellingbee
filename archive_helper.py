from datetime import date
from os import path
from os import listdir
from typing import List
import pickle
import importlib


class ArchiveHelper:
    game_file_prefix = 'bee'
    game_file_extension = '.pkl'
    json_file_prefix = 'json'
    json_file_extension = '.txt'

    game_archive_path = path.abspath(path.join('archive', 'games'))
    json_archive_path = path.abspath(path.join('archive', 'json'))

    @staticmethod
    def filename_extension(filename: str) -> str:
        return path.splitext(filename)[1]

    @classmethod
    def get_all_filenames(cls) -> List[str]:
        ls_list = listdir(cls.game_archive_path)
        return [filename for filename in ls_list if cls.filename_extension(filename) == cls.game_file_extension]

    @classmethod
    def get_all_file_dates(cls) -> List[date]:
        return [cls.filename_to_date(filename) for filename in cls.get_all_filenames()]

    @classmethod
    def is_game_date_archived(cls, game_date: date):
        return game_date in cls.get_all_file_dates()

    @staticmethod
    def date_to_date_str(game_date: date) -> str:
        return game_date.strftime('%Y-%m-%d')

    @classmethod
    def date_to_game_filename(cls, game_date: date) -> str:
        return game_date.strftime(
            '{0:s}-{1:s}{2:s}'.format(cls.game_file_prefix, cls.date_to_date_str(game_date), cls.game_file_extension))

    @classmethod
    def date_to_game_filepath(cls, game_date: date) -> str:
        return path.join(cls.game_archive_path, cls.date_to_game_filename(game_date))

    @classmethod
    def date_to_json_filename(cls, game_date: date) -> str:
        return game_date.strftime(
            '{0:s}-{1:s}{2:s}'.format(cls.json_file_prefix, cls.date_to_date_str(game_date), cls.json_file_extension))

    @classmethod
    def date_to_json_filepath(cls, game_date: date) -> str:
        return path.join(cls.json_archive_path, cls.date_to_json_filename(game_date))

    @staticmethod
    def filename_to_date_str(filename: str) -> str:
        return '-'.join(path.splitext(filename)[0].split('-')[1:])

    @classmethod
    def filename_to_date(cls, filename: str) -> date:
        return date(*(int(num_str) for num_str in cls.filename_to_date_str(filename).split('-')))


class PickleProtocol:
    def __init__(self, level):
        self.previous = pickle.HIGHEST_PROTOCOL
        self.level = level

    def __enter__(self):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.level

    def __exit__(self, *exc):
        importlib.reload(pickle)
        pickle.HIGHEST_PROTOCOL = self.previous
