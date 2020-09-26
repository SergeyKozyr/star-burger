import requests
import os
from dotenv import load_dotenv
from geopy import distance as gp_distance
from decimal import Decimal

load_dotenv()
yandex_apikey = os.environ['YANDEX_API_KEY']


def fetch_coordinates(place, apikey=yandex_apikey):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode": place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    places_found = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = places_found[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(place_1, place_2):
    distance = Decimal(gp_distance.distance(place_1, place_2).km)
    return round(distance, 3)
