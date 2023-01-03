from datetime import datetime as date_time
from datetime import date
from enum import Enum
import requests
import json


class CrawledJson:

    def __init__(self, json_dict: dict):
        self._json_dict = json_dict

    @property
    def json_str(self) -> str:
        return json.dumps(self._json_dict)

    @property
    def date_str(self) -> str:
        return self._json_dict['printDate']

    @property
    def date(self) -> date:
        return date_time.strptime(self.date_str, '%Y-%m-%d').date()

    @property
    def center_letter(self) -> str:
        center_letter_key = 'centerLetter'
        return self._json_dict[center_letter_key].upper()

    @property
    def valid_letters(self) -> set:
        valid_letters_key = 'validLetters'
        return {letter.upper() for letter in self._json_dict[valid_letters_key]}

    @property
    def answers(self) -> set:
        answers_key = 'answers'
        return {answer.upper() for answer in self._json_dict[answers_key]}

    @property
    def pangrams(self) -> set:
        pangrams_key = 'pangrams'
        return {pangram.upper() for pangram in self._json_dict[pangrams_key]}


class CrawlerDay(Enum):
    UNKNOWN = 0
    TODAY = 1
    YESTERDAY = 2


class WebCrawler:

    def __init__(self, crawler_day: CrawlerDay = CrawlerDay.TODAY):
        self._parsed_json_dict = {}
        self._day = crawler_day
        self.crawl_data()

    @property
    def day_str(self) -> str:
        return self._day.name.lower()

    @property
    def active_crawled_json(self) -> CrawledJson:
        return CrawledJson(self._parsed_json_dict[self.day_str])

    def set_day(self, crawler_day: CrawlerDay = CrawlerDay.TODAY) -> None:
        self._day = crawler_day

    def crawl_data(self) -> None:
        url = 'https://www.nytimes.com/puzzles/spelling-bee'
        r = requests.get(url)
        url_content_str = r.content.decode('utf-8')
        start_matcher = """{"today":"""
        start_pos = url_content_str.find(start_matcher)
        end_matcher = """"Sam Ezersky"}}"""
        end_pos = url_content_str.find(end_matcher) + len(end_matcher)
        match_json_text = url_content_str[start_pos:end_pos]
        parsed_json_dict = json.loads(match_json_text)
        self._parsed_json_dict = parsed_json_dict
