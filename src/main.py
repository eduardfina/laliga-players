from scraper import PlayersScraper

# output_file = "dataset.csv"

scraper = PlayersScraper()
data = scraper.scrape()
scraper.data2csv(data)

