from bee_interface import *

# Archive today's games
print('Archiving games')
crawler = WebCrawler()
Bee().archive_from_crawler(crawler)

# Start
sb = BeeInterface()
sb.start_game()  # date(2023, 1, 1)
sb.add_guess('GUESS')

sb.save_game(overwrite=True)
