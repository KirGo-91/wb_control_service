import os
import requests
from geopy.geocoders import Nominatim
from datetime import datetime
from core.logger import Logger


class ApiClient:
  def __init__(self, name='ApiClient'):
      self._geo_api_url = os.getenv('GEO_API_URL')
      self._search_api_url = os.getenv('SEARCH_API_URL')
      self._cities = eval(os.getenv('CITIES')) if os.getenv('CITIES') else []
      self._queries = eval(os.getenv('QUERIES')) if os.getenv('QUERIES') else []
      self._brands = eval(os.getenv('BRANDS')) if os.getenv('BRANDS') else []
      self._logger = Logger(name).get_logger()

  def generate_city_params(self, city):
    geolocator = Nominatim(user_agent='abcd')
    location = geolocator.geocode(city)
    if location:
      params = {
                'latitude': location.latitude,
                'longitude': location.longitude,
                'address': city
                }
      city_params_response = requests.get(self._geo_api_url, params=params)
      if city_params_response.status_code == 200:
        return city_params_response.json()
      else:
        self._logger.error(f"Ошибка получения данных для города {city}: {city_params_response.status_code}")
    else:
      self._logger.warning(f"Геолокация для города {city} не найдена")
    return {}
  
  def get_city_params(self):
    self._logger.info('Запрос геоданных с API WB')
    city_info = {}
    try:
      for city in self._cities:
        data = self.generate_city_params(city)
        city_info[city] = data.get('xinfo') if data else None
      self._logger.info(f'Геоданные по городам {self._cities} получены')
    except requests.exceptions.RequestException as ex:
      self._logger.error(f'Ошибка соединения с API WB: {ex}')
    return city_info

  def get_data(self): 
    try:
      max_page = 2 
      arr = []
      dt = datetime.now()
      city_info = self.get_city_params()
      self._logger.info('Запрос данных по товарам с API WB')

      for city in self._cities:
        city_params = city_info.get(city, '')
        if not city_params:
          self._logger.warning(f"Отсутствуют параметры для города {city}, пропуск.")
          continue
        
        for query in self._queries:
          pos = 0

          for page in range(1, max_page+1):
            url = f'''
            {self._search_api_url}?
            ab_testing=false&
            ab_vector_qi_from=vec_search_new_model&
            inheritFilters=false&
            lang=ru&
            page={page}&
            query={query}&
            resultset=catalog&
            sort=popular&
            suppressSpellcheck=false&
            uclusters=0&
            {city_params}
            '''.replace('\n', '').replace(' ', '').strip()

            # Можно добавить headers, если API требует
            # headers={
            #  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36")
            # }
            res = requests.get(url) # , headers=headers)

            if res.status_code == 200:
              data = res.json()
              products = data.get('products', [])

              for card in products:
                pos += 1

                if card['brand'] in self._brands:
                  price = card.get('sizes', [{}])[0]['price']['basic'] / 1000 if card.get('sizes') else -1
                  arr.append([
                            card['name'],
                            card['brand'],
                            pos,
                            price,
                            dt,
                            query,
                            city
                          ])
            else:
              self._logger.warning(f"Ошибка запроса: статус {res.status_code}")
      self._logger.info(f'Общее количество собранных записей удовлетворяющих запросу: {len(arr)}')
      return arr
    except requests.exceptions.RequestException as ex:
      self._logger.error(f'Ошибка соединения с API WB: {ex}')
      return [] 