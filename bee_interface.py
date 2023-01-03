from bee_engine import *
import numpy as np
import pandas as pd


class BeeInterface(Bee):
    _columns = 5
    _tiers = [0.7, 0.8, 0.9, 0.95, np.inf]

    @property
    def number_of_letter_hints(self) -> int:
        progress_tiers_bool_vals = (self._progress < tier for tier in self._tiers)
        return next((ind for ind, bool_val in enumerate(progress_tiers_bool_vals) if bool_val))

    @classmethod
    def print_word_list(cls, header: str, guess_list: List[str]) -> None:
        if bool(header):
            print('{0:s}'.format(header))
        for guess_ind, guess in enumerate(guess_list):
            if guess_ind % cls._columns < cls._columns - 1:
                print('{0: <15}'.format(guess), end='')
            else:
                print(guess, end='\n')
        print('', end='\n')

    def print_guesses(self) -> None:
        affix_guesses = sorted(self._guess_categories[GuessCategory.PREFIX]) + \
                        sorted(self._guess_categories[GuessCategory.SUFFIX])
        self.print_word_list('* COMPONENTS *', affix_guesses)
        self.print_word_list('', sorted(self._guess_categories[GuessCategory.MISSING]))
        self.print_word_list('* CORRECT *', sorted(self._guess_categories[GuessCategory.CORRECT]))

    def print_hints(self) -> None:
        first_n = self.number_of_letter_hints
        remaining_words = sorted(self._answers.difference(self._guess_categories[GuessCategory.CORRECT]))
        letter_len_list = [(word[:first_n], len(word)) for word in remaining_words]
        columns = ['Letter', 'Length']
        print(pd.DataFrame(letter_len_list, columns=columns).groupby(columns).apply(len))

    def print_output(self) -> None:
        self.print_guesses()
        self.print_hints()

    def new_guess(self, guess: str) -> None:
        self.add_guess(guess)
        self.print_output()
