from urllib.request import urlopen
import re
import time
from bs4 import BeautifulSoup
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


class PlayersScraper():

    def __init__(self):
        self.urls = ["https://www.marca.com/futbol/primera-division/clasificacion.html",
                     "https://www.marca.com/futbol/segunda-division/clasificacion.html"]
        self.data = []

    def __get_team_links(self, url):
        timeout = 10
        driver = webdriver.Chrome()  # Open Chromium instance where the code and shadow-root can be processed
        driver.implicitly_wait(timeout)  # Set timeout before run command, it give the time at the DOM to self create

        driver.get(url)  # Open Chrome page at request url

        # With the CSS_SELECTOR (using ID and tag_name) the code travel through the DOM.
        shadow_host_1 = driver.find_element(By.CSS_SELECTOR, 'ue-table-ranking')
        shadow_root_1 = shadow_host_1.shadow_root

        shadow_host_2 = shadow_root_1.find_element(By.CSS_SELECTOR, 'ue-table-ranking-extended')
        shadow_root_2 = shadow_host_2.shadow_root

        # Finally reach the target Shadow DOM tree, simply search the correct tag and export the HTML data
        elements = shadow_root_2.find_elements(By.CLASS_NAME, "ue-c-table-ranking__team-link")
        links = [elem.get_attribute('href') for elem in elements]


        return links

    def __download_html(self, url):
        response = urlopen(url)
        html = response.read()
        return html
    def __get_squad_link(self, url):
        html = self.__download_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        squad = soup.find(lambda tag: tag.name == "a" and "Plantilla" in tag.text)
        link = squad["href"]

        return link

    def __get_player_links(self, url):
        html = self.__download_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        players = [h3.find("a") for h3 in soup.findAll('h3', class_="ue-c-sports-card__title")]
        player_links = [a["href"] for a in players]

        return player_links
    def scrape(self):
        print('Web Scraping of football players data from https://www.marca.com/')

        # Start timer
        start_time = time.time()

        print('Getting all team links...')

        team_links = []
        for url in self.urls:
            team_links.extend(self.__get_team_links(url))

        print('Getting all squad links...')

        squad_links = []
        for team in team_links:
            squad_links.append(self.__get_squad_link(team))

        print('Getting all player links...')

        player_links = []
        for squad in squad_links:
            player_links.extend(self.__get_player_links(squad))
