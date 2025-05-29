import aiohttp

from fastapi.exceptions import HTTPException


async def check_resp(response: aiohttp.ClientResponse):
    data = await response.json()
    if response.status != 200:
        raise HTTPException(status_code=response.status, detail=data)
    return data


async def get_city_coords(city: str):
    async with aiohttp.ClientSession() as session:
        params = {
            'name': city,
            'language': 'ru',
            'count': 1
        }
        url = f'https://geocoding-api.open-meteo.com/v1/search'
        async with session.get(url=url, params=params) as response:
            json = await check_resp(response)
            response_data = json['results'][0]
            lat, lon, city, country_code = response_data['latitude'], response_data[
                'longitude'], response_data['name'], response_data['country_code']
            dataseq = [lat, lon, city, country_code]
            if not all(dataseq):
                raise HTTPException(status_code=response.status, detail={
                                    'error': f'Data that could not be retrieved: {[val for val in dataseq if not val]}'})
            return dataseq


async def get_forecast(city: str) -> dict:
    lat, lon, formatted_city_name, country = await get_city_coords(city)
    async with aiohttp.ClientSession() as session:
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum',
            'timezone': 'auto',
            'forecast_days': 3
        }
        url = 'https://api.open-meteo.com/v1/forecast'
        async with session.get(url=url, params=params) as response:
            response_data = await check_resp(response)
            return response_data, {'city_name': formatted_city_name, 'country_code': country}


weather_codes_mapping = {
    0: 'Ясно',
    1: 'Преимущественно ясно',
    2: 'Переменная облачность',
    3: 'Пасмурно',
    45: 'Туман',
    48: 'Иней',
    51: 'Слабая морось',
    53: 'Умеренная морось',
    55: 'Сильная морось',
    56: 'Слабая ледяная морось',
    57: 'Сильная ледяная морось',
    61: 'Слабый дождь',
    63: 'Умеренный дождь',
    65: 'Сильный дождь',
    66: 'Слабый ледяной дождь',
    67: 'Ледяной ливень',
    71: 'Слабый снег',
    73: 'Умеренный снег',
    75: 'Сильный снег',
    77: 'Град',
    80: 'Слабый ливень',
    81: 'Умеренный ливень',
    82: 'Сильный ливень',
    85: 'Легкий снегопад',
    86: 'Сильный снегопад',
    95: 'Гроза',
    96: 'Гроза со слабым градом',
    99: 'Гроза с сильным градом',
}


def extract_data(forecast: dict) -> dict:
    daily_forecasts = forecast['daily']
    dates = daily_forecasts['time']
    weather_codes = daily_forecasts['weather_code']
    t_mins = daily_forecasts['temperature_2m_min']
    t_maxes = daily_forecasts['temperature_2m_max']
    percipitations = daily_forecasts['precipitation_sum']
    result = {date: {'cloudiness': None, 'Tmin': None,
                     'Tmax': None, 'percipitation': None} for date in dates}
    for i in range(len(dates)):
        date = dates[i]
        result[date].update({'cloudiness': weather_codes_mapping[weather_codes[i]], 'Tmin': t_mins[i],
                            'Tmax': t_maxes[i], 'percipitation': percipitations[i]})
    return result
