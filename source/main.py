from scraper import PlayersScraper

scraper = PlayersScraper()
data = scraper.scrape()
scraper.data2csv(data)

