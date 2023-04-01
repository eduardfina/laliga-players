import csv
from urllib.request import urlopen
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


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

    def __get_player_stats_link(self, url):
        html = self.__download_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        squad = soup.find(lambda tag: tag.name == "a" and "Estadísticas" in tag.text)
        if squad is not None:
            link = squad["href"]
        else:
            link = 0

        return link

    def __get_player_basic_info(self, url):
        player_info = {}
        html = self.__download_html(url)
        soup = BeautifulSoup(html, 'html.parser')

        info = [tag.text for tag in soup.findAll('ul', class_="ue-c-sports-card__list")]

        player_info["playerName"] = re.search("\n\n(.*,)", info[0])[1]

        try:
            height_and_weight = re.search("1.*kg", info[0])[0]
            if height_and_weight is not None:
                player_info["height"] = height_and_weight.split(",")[0]
                player_info["weight"] = height_and_weight.split(",")[1].replace(" ", "", 1)
        except:
            player_info["height"] = ""
            player_info["weight"] = ""

        try:

            birth_and_country = re.search("[0-9]{1,2}.*[0-9]{4}.*", info[0])[0]
            if re.match("en", birth_and_country):
                player_info["birthDate"] = birth_and_country.split(" en ")[0]
                player_info["country"] = birth_and_country.split(" en ")[1].replace(" ", "").replace(".", "")
            else:
                player_info["birthDate"] = birth_and_country.split(",")[0]
                player_info["country"] = birth_and_country.split(",")[1].replace(" ", "").replace(".", "")

        except:
            player_info["birthDate"] = ""
            player_info["country"] = ""

        return player_info

    def __get_stats(self, url, players_info, player_name):

        attributes = ["goals", "shots", "penalties", "foulsReceived", "offSides", "foulsCommited", "recoveries",
                      "passesCutOff", "entrancesWon", "duels", "cards", "passes", "goalAssists", "dribbles",
                      "corners", "ballLosses"]

        try:
            html = self.__download_html(url)  # Marca shows the club stats by default!
            soup = BeautifulSoup(html, 'html.parser')

            info = [tag.text for tag in
                    soup.findAll('tr', class_="ue-c-sports-table__row ue-c-sports-table__row--main")]

            if len(info) == 0:
                for attribute in attributes:
                    players_info[player_name][attribute] = "0"
            else:
                for item in info:
                    if "Goles" in item:
                        players_info[player_name]["goals"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Tiros a puerta" in item:
                        players_info[player_name]["shots"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Penaltis a favor" in item:
                        players_info[player_name]["penalties"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Faltas recibidas" in item:
                        players_info[player_name]["foulsReceived"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Fueras de juego" in item:
                        players_info[player_name]["offSides"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Faltas cometidas" in item:
                        players_info[player_name]["foulsCommited"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Recuperaciones" in item:
                        players_info[player_name]["recoveries"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Pases cortados" in item:
                        players_info[player_name]["passesCutOff"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Entradas ganadas" in item:
                        players_info[player_name]["entrancesWon"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Duelos" in item:
                        players_info[player_name]["duels"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Tarjetas" in item:
                        players_info[player_name]["cards"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Pases" in item:
                        players_info[player_name]["passes"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Asistencias de gol" in item:
                        players_info[player_name]["goalAssists"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Regates" in item:
                        players_info[player_name]["dribbles"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Centros y corners" in item:
                        players_info[player_name]["corners"] = re.search("\n([0-9]+)\n", item)[1]

                    if "Pérdidas de balón" in item:
                        players_info[player_name]["ballLosses"] = re.search("\n([0-9]+)\n", item)[1]
        except:
            attributes = ["goals", "shots", "penalties", "foulsReceived", "offSides", "foulsCommited", "recoveries",
                          "passesCutOff", "entrancesWon", "duels", "cards", "passes", "goalAssists", "dribbles",
                          "corners", "ballLosses"]

            for attribute in attributes:
                players_info[player_name][attribute] = "NA"

        return players_info

    def data2csv(self, data):
        with open("../dataset/dataset.csv", "w", newline="") as csvfile:
            print("Creating CSV...")
            writer = csv.writer(csvfile)

            # Header
            header = ["playerName", "height", "weight", "birthDate", "country", "url", "goals", "shots", "penalties",
                      "foulsReceived", "offSides", "foulsCommited", "recoveries", "passesCutOff", "entrancesWon",
                      "duels", "cards", "passes", "goalAssists", "dribbles", "corners", "ballLosses"]
            writer.writerow(header)

            # Data
            for player, data in data.items():
                row = [player] + list(data.values())
                writer.writerow(row)
            print("Done.")

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

        players_info = {}
        print("Scraping each player information...")

        for url in player_links:
            player_info = self.__get_player_basic_info(url)
            player_name = player_info["playerName"].replace(",", "")
            print(player_name)

            players_info[player_name] = {k: v for k, v in player_info.items() if k != "playerName"}
            players_info[player_name]["url"] = url

            player_stats_url = self.__get_player_stats_link(url)
            if player_stats_url != "":
                players_info = self.__get_stats(player_stats_url, players_info, player_name)

        end_time = time.time()
        scraping_time = end_time - start_time
        print("Done in " + str(scraping_time) + "seconds.")

        # print(players_info)
        return players_info
