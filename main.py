import requests
import os
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
KM_IN_DEGREE = 111.139
ZOOM = 10
DEFAULT_SQUARE_RANGE = 30


class City:
    """
    Create city object to request temperature of city and
    average temperature of square area
    """

    def __init__(self, name, square_range=DEFAULT_SQUARE_RANGE):
        """
        :param name: City name in english or local language
        :param square_range: Distance to right border of square
        """
        self.name = name
        self.square_range = float(square_range)
        self.raw_data = self.get_city_by_name()
        self.coordinates = self.raw_data.get('coord')
        main_section = self.raw_data.get('main', 'City not found!')
        if main_section != 'City not found!':
            self.temp = main_section.get('temp', 'City not found')
        else:
            # TODO: Find a better way than default 0.0 Raise!
            self.temp = 0.0
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
    try:
        with open(file_name, 'r', encoding='utf8') as f:
            data = f.readlines()
        cities = []
        for item in data:
            item = item.rstrip().split(';')
            cities.append(City(item[0], int(item[1])))
        return cities
    except FileNotFoundError:
        return False


if __name__ == '__main__':

    while True:
        print('\n\nEnter city to request temperature (ex: "Moscow")\n'
              'or "city;range" to find average temperature (ex: "Tver;30")\n'
              'or filename.txt (";"-separated) to sort by average (ex: "cities.txt")\n'
              'or "q" to exit')
        user_value = input()

        if user_value == 'q':
            break
        elif user_value[-4:] == '.txt':
            list_of_city_objects = get_cities_from_file(user_value)
            if list_of_city_objects is not False:
                list_of_city_objects = sorted(list_of_city_objects, key=lambda city: city.get_square_temperature())
                for city_obj in list_of_city_objects:
                    print(city_obj)
            else:
                print('File not found')
        elif ';' in user_value:
            current_city, range_ = user_value.split(';')
            current_city_obj = City(name=current_city, square_range=range_)
            print(f'Temp in {current_city_obj.name} is {current_city_obj.temp}')
            print(
                f'Avg temp in square around {current_city_obj.name} is {current_city_obj.get_square_temperature():.1f}')
        else:
            current_city = user_value
            current_city_obj = City(name=current_city)
            print(f'Temp in {current_city_obj.name} is {current_city_obj.temp}')
