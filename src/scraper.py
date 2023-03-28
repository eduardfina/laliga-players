import urllib2
import re
import time
from bs4 import BeautifulSoup
from dateutil import parser
from geopy.geocoders import Yandex

class PlayersScraper():

    def __init__(self):
        self.url = "https://www.marca.com/futbol/primera-division/clasificacion.html"
        self.subdomain = ""
        self.data = []