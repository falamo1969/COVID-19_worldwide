from scraper import CovidScraper

fichero = "csv/info_covid.csv"

scraper = CovidScraper()
scraper.scrap_info_covid()
scraper.scrap_write_csv(fichero)