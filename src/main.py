from scraper import PlayersScraper

# output_file = "dataset.dataset"

scraper = PlayersScraper()
data = scraper.scrape()
scraper.data2csv(data)

