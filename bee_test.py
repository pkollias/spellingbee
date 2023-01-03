import unittest
from webcrawler import *
from archive_helper import *
from bee_engine import *


class ArchiverTestCase(unittest.TestCase):
    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

# customization on setting up a test case suite,
#                  wrapping a test with custom functions besides class setUp and tearDown
# custom test skipping and setting expected fails
# subtests allow unit test to continue and test different configurations of a parameter for different test iterations
