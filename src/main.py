from scraper import PlayersScraper

output_file = "dataset.csv"

scraper = PlayersScraper();
scraper.scrape();
scraper.data2csv(output_file);
