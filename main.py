import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
KM_IN_DEGREE = 111.139
ZOOM = 10


class City:
    """
    Create city object to request temperature of city and
    average temperature of square area
    """

    def __init__(self, name, square_range):
        """
        :param name: City name in english or local language
        :param square_range: Distance to right border of square
        """
        self.name = name
        self.square_range = float(square_range)
        self.raw_data = self.get_city_by_name()
        self.coordinates = self.raw_data.get('coord')
        self.temp = self.raw_data.get('main').get('temp')
        self.square_range_data = {}

    def get_city_by_name(self):
        """
        Get basic info about city weather
        Fire on object creation
        :return: raw json data about city
        """
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": self.name,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
        }
        try:
            response = requests.get(
                url=url,
                params=params,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Не получилось загрузить: {e}"

    def get_cities_within_square(self):
        """
        Get average temperature of cities in rectangle
        Free API limited to 25 queries
        Run by user request
        :return: raw json object with cities
        """
        url = "https://api.openweathermap.org/data/2.5/box/city"
        # calc distance in degrees
        dd = self.square_range / KM_IN_DEGREE
        lon = round(float(self.coordinates.get('lon')), 4)
        lat = round(float(self.coordinates.get('lat')), 4)
        params = {
            "bbox": f"{lon - dd:.4f},{lat - dd:.4f},{lon + dd:.4f},{lat + dd:.4f},{ZOOM}",
            'appid': WEATHER_API_KEY,
            'units': 'metric',
        }

        try:
            response = requests.get(
                url=url,
                params=params,
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return f"Не получилось загрузить: {e}"

    def get_square_temperature(self):
        """
        Calculate average temperature in rectangle area
        :return: average temperature in float
        """
        if not self.square_range_data:
            self.square_range_data = self.get_cities_within_square()
        cities_temp = [city['main']['temp'] for city in self.square_range_data.get('list')]
        return sum(cities_temp) / len(cities_temp)

    def __repr__(self):
        return f'{self.name} with {self.square_range} km square and now: {self.temp}C'


def get_cities_from_file(file_name):
    """
    Load cities from file to list of objects
    :param file_name: file name
    :return: list of City class objects
    """
    with open(file_name, 'r', encoding='utf8') as f:
        data = f.readlines()
    cities = []
    for item in data:
        item = item.rstrip().split(';')
        print(item)
        cities.append(City(item[0], item[1]))
    return cities


if __name__ == '__main__':
    # Test city creation
    moscow = City(name='Москва', square_range='100')
    # Test if temperature is requested
    print(f'Temp in {moscow.name} is {moscow.temp}')
    # Test if average temperature is calculated (limited to 25 requests via free API)
    # print(f'Avg temp in square around {moscow.name} is {moscow.get_square_temperature():.1f}')

    # Test list object list creation
    list_of_city_objects = get_cities_from_file('cities.txt')
    # Sort by city temp. Original task ask for average sorting but free API has limitations
    list_of_city_objects = sorted(list_of_city_objects, key=lambda city: city.temp)
    # list_of_city_objects = sorted(list_of_city_objects, key=lambda city: city.get_square_temperature())

    # Print list of sorted objects in nice way thanks to __repr__ method
    for city_obj in list_of_city_objects:
        print(city_obj)
