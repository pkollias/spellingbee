from __future__ import annotations
from warnings import warn
from warnings import simplefilter
from typing import Union
from webcrawler import *
from archive_helper import *

simplefilter('always', UserWarning)


class GuessCategory(Enum):
    ERROR = 0
    UNKNOWN = -1
    PREFIX = 1
    SUFFIX = 2
    CORRECT = 3
    MISSING = 4


class BeeLetters:

    def __init__(self, letters: set = set(), center_letter: str = '') -> None:
        self._valid_letters = letters
        self._center_letter = center_letter

    def __str__(self):
        return '-'.join((self._center_letter, ''.join(sorted(self._non_center_letters))))

    def __repr__(self):
        repr_str = "{0:s} object at {1:s}:\n".format(str(self.__class__), hex(id(self))) + \
                   "center_letter: {0:s}\n".format(str(self._center_letter)) + \
                   "non_center_letters: {0:s}".format(''.join(sorted(self._non_center_letters)))
        return repr_str

    @property
    def _non_center_letters(self):
        return self._valid_letters.difference(set(self._center_letter))

    def is_valid_word(self, word_str: str) -> bool:
        # word_str = word_str.upper()
        all_letters_valid = all([letter in self._valid_letters for letter in word_str])
        return all_letters_valid


class Bee:
    _archive_helper = ArchiveHelper()

    def __init__(self, game_date: Union[date, None] = None, letters: BeeLetters = BeeLetters(), answers: set = set(),
                 guesses: List[str] = []):
        self._date = game_date
        self._letters = letters
        self._answers = answers
        self._guesses = set()
        self._guess_categories = {GuessCategory.PREFIX: set(),
                                  GuessCategory.SUFFIX: set(),
                                  GuessCategory.CORRECT: set(),
                                  GuessCategory.MISSING: set(),
                                  GuessCategory.ERROR: set()}
        self._last_guess = None
        self._store_errors = False
        self.add_guesses(guesses)

    def init_from_json_str(self, json_str) -> None:
        crawled_json = CrawledJson(json.loads(json_str))
        self._date = crawled_json.date
        self._letters = BeeLetters(crawled_json.valid_letters, crawled_json.center_letter)
        self._answers = crawled_json.answers

    def init_from_bee(self, bee: Bee) -> None:
        self._date = bee._date
        self._letters = bee._letters
        self._answers = bee._answers
        self._guesses = bee._guesses
        self._guess_categories = bee._guess_categories
        self._store_errors = bee._store_errors

    def __str__(self):
        return 'Bee({0:s}, \'{1:s}\')'.format(str(self._date), str(self._letters))

    def __repr__(self):
        repr_str = "{0:s} object at {1:s}:\n".format(str(self.__class__), hex(id(self))) + \
                   "date: {0:s}\n".format(str(self._date)) + \
                   "letters: {0:s}\n".format(str(self._letters)) + \
                   "answers count: {0:d}\n".format(len(self._answers)) + \
                   "initiated: {0:s}".format(str(bool(self._guesses))) + \
                   "progress: {0:.2f}".format(self._progress)
        return repr_str

    @property
    def _sorted_guesses(self) -> List[str]:
        return sorted(self._guesses)

    @property
    def _progress(self) -> float:
        return len(self._guess_categories[GuessCategory.CORRECT]) / len(self._answers)

    # Guesses API.

    def classify_word(self, word_str: str) -> GuessCategory:
        # word_str = word_str.upper()
        # Check if word is already in guesses.
        if word_str in self._guesses:
            warn('Word already in guesses ({0:s})'.format(word_str))
        # Classify word.
        if word_str[-1] == '-' and self._letters.is_valid_word(word_str[:-1]):
            return GuessCategory.PREFIX
        elif word_str[0] == '-' and self._letters.is_valid_word(word_str[1:]):
            return GuessCategory.SUFFIX
        elif word_str in self._answers:
            return GuessCategory.CORRECT
        elif self._letters.is_valid_word(word_str):
            return GuessCategory.MISSING
        else:
            warn('Not valid entry ({0:s})'.format(word_str))
            return GuessCategory.ERROR

    def add_guess(self, guess: str) -> None:
        guess = guess.upper()
        guess_category = self.classify_word(guess)
        if guess_category != GuessCategory.ERROR or self._store_errors:
            self._guesses.add(guess)
            self._guess_categories[guess_category].add(guess)
            self._last_guess = guess

    def add_guesses(self, guesses: List[str]) -> None:
        for guess in sorted(guesses):
            self.add_guess(guess)

    def remove_last_guess(self) -> None:
        guess = self._last_guess
        if guess is not None:
            guess_category = self.classify_word(guess)
            if guess_category != GuessCategory.ERROR or self._store_errors:
                self._guesses.remove(guess)
                self._guess_categories[guess_category].remove(guess)
                self._last_guess = None

    def clear_error_guesses(self) -> None:
        for guess in self._guess_categories[GuessCategory.ERROR]:
            self._guesses.remove(guess)
            self._guess_categories[GuessCategory.ERROR].remove(guess)

    def reset_game(self) -> None:
        self._guesses = set()
        self._guess_categories = {GuessCategory.PREFIX: set(),
                                  GuessCategory.SUFFIX: set(),
                                  GuessCategory.CORRECT: set(),
                                  GuessCategory.MISSING: set(),
                                  GuessCategory.ERROR: set()}

    # Archive

    def save_game(self, overwrite: bool = True) -> None:
        if self._date not in self._archive_helper.get_all_file_dates() or overwrite:
            with PickleProtocol(pickle.HIGHEST_PROTOCOL):
                with open(self._archive_helper.date_to_game_filepath(self._date), 'wb') as f:
                    pickle.Pickler(f).dump(self)

    def save_json_str(self, json_str: str) -> None:
        with open(self._archive_helper.date_to_json_filepath(self._date), 'w') as f:
            f.write(json_str)

    @staticmethod
    def archive_from_crawler(crawler: WebCrawler, overwrite: bool = False) -> None:
        for crawler_day in [CrawlerDay.TODAY, CrawlerDay.YESTERDAY]:
            crawler.set_day(crawler_day)
            bee = Bee()
            bee.init_from_json_str(crawler.active_crawled_json.json_str)
            bee.save_game(overwrite=overwrite)
            bee.save_json_str(crawler.active_crawled_json.json_str)

    def load_game(self, game_date: date) -> None:
        with PickleProtocol(pickle.HIGHEST_PROTOCOL):
            with open(self._archive_helper.date_to_game_filepath(game_date), 'rb') as f:
                self.init_from_bee(pickle.load(f))

    @classmethod
    def load_json_str(cls, game_date: date) -> str:
        with open(cls._archive_helper.date_to_json_filepath(game_date), 'r') as f:
            return f.read()

    # Game API.

    def start_game(self, game_date: date = date.today()) -> None:
        self.load_game(game_date)
